import os
import shutil
import face_recognition
import numpy as np
from pathlib import Path
from datetime import datetime
from django.conf import settings
from database.models import Student, TrainingSession, Subject
from users.models import User
from .utils import EncodingStore
import cv2

class AutoTrainingService:
    def __init__(self):
        self.base_training_dir = Path(settings.MEDIA_ROOT) / 'training_data'
        self.base_training_dir.mkdir(parents=True, exist_ok=True)
        
    def create_training_folder(self, student_code, full_name):
        """Tạo folder training theo format student_code_fullname"""
        folder_name = f"{student_code}_{full_name.replace(' ', '_')}"
        folder_path = self.base_training_dir / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)
        return folder_path
    
    def process_training_images(self, student_id, subject_id, images):
        """Xử lý training với nhiều ảnh"""
        try:
            student = Student.objects.get(id=student_id)
            subject = Subject.objects.get(id=subject_id)
            
            # Tạo folder training
            folder_path = self.create_training_folder(student.student_code, student.name)
            
            # Tạo training session
            training_session = TrainingSession.objects.create(
                student=student,
                subject=subject,
                folder_path=str(folder_path),
                status='processing'
            )
            
            # Lưu và xử lý ảnh
            saved_images = []
            for i, image in enumerate(images):
                # Lưu ảnh
                image_name = f"training_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                image_path = folder_path / image_name
                
                with open(image_path, 'wb') as f:
                    for chunk in image.chunks():
                        f.write(chunk)
                
                saved_images.append(str(image_path))
            
            # Cập nhật số lượng ảnh
            training_session.images_count = len(saved_images)
            training_session.save()
            
            # Tạo encoding từ ảnh
            encodings = self._create_encodings(saved_images)
            
            # Lưu encodings
            if encodings:
                self._save_encodings(student.student_code, encodings)
                training_session.status = 'completed'
                training_session.save()
                return {
                    'success': True,
                    'message': f'Training thành công cho {student.name}',
                    'folder_path': str(folder_path),
                    'images_count': len(saved_images)
                }
            else:
                training_session.status = 'failed'
                training_session.save()
                return {
                    'success': False,
                    'message': 'Không thể tạo encoding từ ảnh'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Lỗi: {str(e)}'
            }
    
    def _create_encodings(self, image_paths):
        """Tạo encodings từ danh sách ảnh"""
        encodings = []
        for image_path in image_paths:
            try:
                # Đọc ảnh
                image = face_recognition.load_image_file(image_path)
                # Detect faces
                face_encodings = face_recognition.face_encodings(image)
                
                if face_encodings:
                    # Lấy encoding đầu tiên (giả sử chỉ có 1 khuôn mặt)
                    encodings.append(face_encodings[0])
                    
            except Exception as e:
                print(f"Lỗi xử lý ảnh {image_path}: {e}")
                continue
        
        return encodings
    
    def _save_encodings(self, student_code, encodings):
        """Lưu encodings vào file"""
        encodings_dir = Path(settings.MEDIA_ROOT) / 'encodings'
        encodings_dir.mkdir(parents=True, exist_ok=True)
        
        encodings_file = encodings_dir / f"{student_code}_encodings.npy"
        np.save(str(encodings_file), encodings)
    
    def get_training_status(self, student_id):
        """Lấy trạng thái training của student"""
        try:
            sessions = TrainingSession.objects.filter(student_id=student_id).order_by('-created_at')
            if sessions.exists():
                latest_session = sessions.first()
                return {
                    'status': latest_session.status,
                    'folder_path': latest_session.folder_path,
                    'images_count': latest_session.images_count,
                    'created_at': latest_session.created_at
                }
            return None
        except Exception as e:
            return None

class AttendanceWithConfidence:
    """Service cải tiến cho attendance với confidence score"""
    
    def __init__(self):
        self.encodings_dir = Path(settings.MEDIA_ROOT) / 'encodings'
        self.attendance_images_dir = Path(settings.MEDIA_ROOT) / 'attendance_images'
        self.attendance_images_dir.mkdir(parents=True, exist_ok=True)
    
    def process_attendance(self, image, subject_name, detected_by_user=None, student_code=None):
        """Xử lý attendance với confidence score"""
        try:
            # Lưu ảnh attendance
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_name = f"attendance_{timestamp}.jpg"
            image_path = self.attendance_images_dir / image_name
            
            with open(image_path, 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            
            # Tìm student theo student_code
            try:
                student = Student.objects.get(student_code=student_code)
            except Student.DoesNotExist:
                return {
                    'success': False,
                    'message': f'Không tìm thấy sinh viên với mã số {student_code}'
                }
            
            # Đọc ảnh và detect faces
            image_array = face_recognition.load_image_file(str(image_path))
            face_locations = face_recognition.face_locations(image_array)
            face_encodings = face_recognition.face_encodings(image_array, face_locations)
            
            if not face_encodings:
                return {
                    'success': False,
                    'message': 'Không phát hiện được khuôn mặt trong ảnh'
                }
            
            # So sánh với encoding của student
            best_match = self._find_best_match(face_encodings[0], student_code)
            
            if best_match:
                confidence_percentage = (1 - best_match) * 100
                
                # Tạo attendance record
                attendance = Attendance.objects.create(
                    student=student,
                    subject=subject_name,
                    status='present',
                    face_detection_confidence=confidence_percentage,
                    detected_by=detected_by_user,
                    image_path=str(image_path)
                )
                
                return {
                    'success': True,
                    'message': f'Điểm danh thành công cho {student.name}',
                    'student_code': student_code,
                    'student_name': student.name,
                    'confidence': round(confidence_percentage, 2),
                    'status': 'present'
                }
            else:
                return {
                    'success': False,
                    'message': 'Khuôn mặt không khớp với dữ liệu đã đăng ký'
                }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Lỗi: {str(e)}'
            }
    
    def _find_best_match(self, face_encoding, student_code):
        """Tìm encoding của student cụ thể"""
        try:
            enc_file = self.encodings_dir / f"{student_code}_encodings.npy"
            
            if not enc_file.exists():
                return None
            
            stored_encodings = np.load(str(enc_file))
            distances = face_recognition.face_distance(stored_encodings, face_encoding)
            
            min_distance = np.min(distances)
            if min_distance < 0.6:  # Threshold
                return min_distance
            else:
                return None
                
        except Exception as e:
            print(f"Lỗi đọc encoding file cho {student_code}: {e}")
            return None 