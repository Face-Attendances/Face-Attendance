# detection/services.py

from pathlib import Path
import cv2
import face_recognition
import pickle
import numpy as np
import csv
from django.conf import settings
from django.core.files.base import ContentFile
from database.models import Student, Subject, Attendance
from datetime import datetime
import logging
from .auto_training import AutoTrainingService

logger = logging.getLogger(__name__)

class FaceRecognitionService:
    def __init__(self):
        self.encodings_path = Path(settings.BASE_DIR) / "training" / "encodings.pickle"
        self.distance_threshold = 0.4  # Stricter threshold for better security
        self.known_encodings = []
        self.known_labels = []
        self.auto_trainer = AutoTrainingService()
        self.load_encodings()
    
    def load_encodings(self):
        """Load trained face encodings from pickle file"""
        try:
            if self.encodings_path.exists():
                with open(self.encodings_path, "rb") as f:
                    data = pickle.load(f)
                    self.known_encodings = data.get("encodings", [])
                    self.known_labels = data.get("labels", [])
                logger.info(f"Loaded {len(self.known_encodings)} face encodings")
            else:
                logger.warning(f"Encodings file not found at {self.encodings_path}")
        except Exception as e:
            logger.error(f"Error loading encodings: {e}")
    
    def verify_student_attendance_with_auto_training(self, image_array, student_code, subject_id):
        """
        Improved attendance verification with auto-training for first-time users
        """
        try:
            # Get student information
            try:
                student = Student.objects.get(student_code=student_code)
            except Student.DoesNotExist:
                return False, "Student not found", None
            
            # Get subject information
            try:
                subject = Subject.objects.get(id=subject_id)
            except Subject.DoesNotExist:
                return False, "Subject not found", None
            
            # Check if this is first-time attendance (no training data)
            student_has_training = self.student_has_training_data(student_code, student.full_name)
            
            if not student_has_training:
                # First-time attendance - save image and auto-train
                logger.info(f"First-time attendance for {student.full_name} ({student_code})")
                
                train_success, train_message = self.auto_trainer.save_first_attendance_image(
                    image_array, student_code, student.full_name
                )
                
                if not train_success:
                    return False, f"First-time setup failed: {train_message}", None
                
                # Reload encodings after training
                self.load_encodings()
                
                # Create attendance record for first time
                attendance = self.create_attendance_record(student, subject)
                if attendance:
                    return True, f"First-time attendance successful! Face training completed. {train_message}", attendance
                else:
                    return False, "Failed to create attendance record", None
            
            else:
                # Existing user - strict verification
                is_verified, message, confidence = self.auto_trainer.verify_student_face_strict(
                    image_array, student_code, student.full_name
                )
                
                if not is_verified:
                    return False, f"Face verification failed: {message}", None
                
                # Check if already attended today
                today = datetime.now().date()
                existing_attendance = Attendance.objects.filter(
                    student=student,
                    subject=subject,
                    attendance_date__date=today
                ).first()
                
                if existing_attendance:
                    return False, "Already marked attendance for today", existing_attendance
                
                # Create attendance record
                attendance = self.create_attendance_record(student, subject)
                if attendance:
                    return True, f"Attendance verified successfully! Confidence: {confidence:.2%}", attendance
                else:
                    return False, "Failed to create attendance record", None
                
        except Exception as e:
            logger.error(f"Error in verify_student_attendance_with_auto_training: {e}")
            return False, f"System error: {str(e)}", None
    
    def student_has_training_data(self, student_code, full_name):
        """Check if student already has training data"""
        try:
            if not self.known_labels:
                return False
            
            # Check if any label matches this student - Updated for dash format
            search_patterns = [
                f"{student_code}-{full_name}".lower(),  # New dash format
                f"{student_code}_{full_name}".lower(),  # Old underscore format
                student_code.lower(),
                full_name.lower()
            ]
            
            for label in self.known_labels:
                label_lower = label.lower()
                for pattern in search_patterns:
                    if pattern in label_lower or label_lower in pattern:
                        logger.info(f"Found existing training data for {full_name} - label: {label}")
                        return True
            
            logger.info(f"No training data found for {full_name} (Code: {student_code})")
            logger.info(f"Available labels: {self.known_labels}")
            return False
            
        except Exception as e:
            logger.error(f"Error checking training data: {e}")
            return False
    
    def create_attendance_record(self, student, subject):
        """Create attendance record with proper error handling"""
        try:
            # Simple approach: create attendance without class_id (allow null)
            attendance = Attendance.objects.create(
                student=student,
                subject=subject,
                attendance_date=datetime.now(),
                status='present'
                # class_id is optional (null=True in model)
            )
            
            logger.info(f"Created attendance record for {student.full_name}")
            return attendance
            
        except Exception as e:
            logger.error(f"Error creating attendance record: {e}")
            return None
    
    def save_attendance_image(self, image_array, student_code, subject_id, success=True):
        """Save the attendance image for record keeping"""
        try:
            # Create directory for attendance images
            attendance_dir = Path(settings.MEDIA_ROOT) / "attendance_images" / student_code
            attendance_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            status_prefix = "success" if success else "failed"
            filename = f"{status_prefix}_attendance_{timestamp}_subject_{subject_id}.jpg"
            
            image_path = attendance_dir / filename
            
            # Save the image
            cv2.imwrite(str(image_path), image_array)
            
            return str(image_path)
            
        except Exception as e:
            logger.error(f"Error saving attendance image: {e}")
            return None

    # Legacy methods for backward compatibility
    def recognize_face(self, image_array):
        """Legacy face recognition method with improved detection"""
        try:
            # Convert image to RGB
            rgb_image = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            
            # Try multiple face detection methods for better accuracy
            face_locations = []
            face_encodings = []
            
            # Method 1: HOG (faster but less accurate)
            face_locations = face_recognition.face_locations(rgb_image, model="hog")
            logger.info(f"HOG detection found {len(face_locations)} faces")
            
            if not face_locations:
                # Method 2: Try with different image preprocessing
                # Adjust brightness and contrast
                enhanced_image = cv2.convertScaleAbs(rgb_image, alpha=1.2, beta=30)
                face_locations = face_recognition.face_locations(enhanced_image, model="hog")
                logger.info(f"Enhanced image detection found {len(face_locations)} faces")
                
                if face_locations:
                    rgb_image = enhanced_image  # Use enhanced image for encoding
            
            if not face_locations:
                # Method 3: Try with different image sizes
                small_image = cv2.resize(rgb_image, (0, 0), fx=0.5, fy=0.5)
                face_locations = face_recognition.face_locations(small_image, model="hog")
                if face_locations:
                    # Scale back the locations
                    face_locations = [(top*2, right*2, bottom*2, left*2) for top, right, bottom, left in face_locations]
                    logger.info(f"Resized image detection found {len(face_locations)} faces")
            
            if not face_locations:
                # Method 4: Try CNN if available (slower but more accurate)
                try:
                    face_locations = face_recognition.face_locations(rgb_image, model="cnn")
                    logger.info(f"CNN detection found {len(face_locations)} faces")
                except Exception as cnn_error:
                    logger.warning(f"CNN detection failed: {cnn_error}")
            
            if not face_locations:
                logger.warning("No face detected in image after trying all methods")
                return False, "No face detected", 0.0
            
            # Get face encodings
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            if not face_encodings:
                logger.warning("No face encodings generated")
                return False, "No face encodings generated", 0.0
            
            if not self.known_encodings:
                logger.warning("No trained faces available")
                return False, "No trained faces available", 0.0
            
            # Use the first face found
            face_encoding = face_encodings[0]
            
            # Calculate distances to all known faces
            distances = face_recognition.face_distance(self.known_encodings, face_encoding)
            
            if len(distances) > 0:
                best_match_index = np.argmin(distances)
                best_distance = distances[best_match_index]
                
                logger.info(f"Face recognition distance: {best_distance:.3f} (threshold: {self.distance_threshold})")
                
                if best_distance < self.distance_threshold:
                    recognized_name = self.known_labels[best_match_index]
                    confidence = 1.0 - best_distance
                    logger.info(f"Face recognized as: {recognized_name} with confidence: {confidence:.3f}")
                    return True, recognized_name, confidence
                else:
                    # Log the closest matches for debugging
                    sorted_indices = np.argsort(distances)
                    logger.info("Closest matches:")
                    for i in range(min(3, len(sorted_indices))):
                        idx = sorted_indices[i]
                        logger.info(f"  {self.known_labels[idx]}: distance = {distances[idx]:.3f}")
            
            logger.info("Face not recognized (distance too high)")
            return False, "Face not recognized", 0.0
            
        except Exception as e:
            logger.error(f"Error in face recognition: {e}")
            return False, f"Recognition error: {str(e)}", 0.0

    def verify_student_attendance(self, image_array, student_code, subject_id):
        """Legacy method - redirects to new auto-training method"""
        return self.verify_student_attendance_with_auto_training(image_array, student_code, subject_id)
