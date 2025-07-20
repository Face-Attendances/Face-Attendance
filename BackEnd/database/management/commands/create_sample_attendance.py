from django.core.management.base import BaseCommand
from database.models import Student, Subject, Attendance, TeacherSubject
from users.models import User
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Create sample attendance data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample attendance data...')
        
        try:
            # Get the teacher and subject from the sample data
            teacher_subject = TeacherSubject.objects.first()
            if not teacher_subject:
                self.stdout.write(
                    self.style.ERROR('No TeacherSubject found. Please run create_sample_data first.')
                )
                return
            
            teacher = teacher_subject.teacher
            subject = teacher_subject.subject
            
            # Get students registered for this subject
            students = Student.objects.filter(
                student_subjects__subject=subject,
                student_subjects__semester=teacher_subject.semester,
                student_subjects__academic_year=teacher_subject.academic_year
            )
            
            if not students.exists():
                self.stdout.write(
                    self.style.ERROR('No students found for this subject. Please run create_sample_data first.')
                )
                return
            
            # Get or create a user for the teacher
            teacher_user, created = User.objects.get_or_create(
                teacher_code=teacher.teacher_code,
                defaults={
                    'username': teacher.teacher_code,
                    'full_name': teacher.name,
                    'email': teacher.email,
                    'role': 'teacher'
                }
            )
            
            # Create attendance records for today
            today = datetime.now().date()
            
            # Create some attendance records
            attendance_created = 0
            
            for student in students:
                # Randomly decide if student attended today
                if random.choice([True, False]):  # 50% chance of attendance
                    # Create attendance record
                    attendance = Attendance.objects.create(
                        student=student,
                        subject=subject,
                        teacher=teacher,
                        status='present',
                        face_detection_confidence=random.uniform(85.0, 98.0),
                        detected_by=teacher_user,
                        timestamp=datetime.now() - timedelta(hours=random.randint(1, 8))
                    )
                    attendance_created += 1
                    self.stdout.write(f'Created attendance for {student.name} - {subject.subject_name}')
            
            # Create some attendance records for yesterday
            yesterday = today - timedelta(days=1)
            
            for student in students:
                if random.choice([True, False]):  # 50% chance of attendance
                    attendance = Attendance.objects.create(
                        student=student,
                        subject=subject,
                        teacher=teacher,
                        status='present',
                        face_detection_confidence=random.uniform(85.0, 98.0),
                        detected_by=teacher_user,
                        timestamp=datetime.combine(yesterday, datetime.min.time()) + timedelta(hours=random.randint(8, 16))
                    )
                    attendance_created += 1
                    self.stdout.write(f'Created yesterday attendance for {student.name} - {subject.subject_name}')
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {attendance_created} attendance records!')
            )
            
            # Print summary
            total_attendance = Attendance.objects.filter(subject=subject).count()
            today_attendance = Attendance.objects.filter(
                subject=subject,
                timestamp__date=today
            ).count()
            
            self.stdout.write(f'\nSummary:')
            self.stdout.write(f'- Total attendance records: {total_attendance}')
            self.stdout.write(f'- Today attendance: {today_attendance}')
            self.stdout.write(f'- Subject: {subject.subject_name}')
            self.stdout.write(f'- Teacher: {teacher.name}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating sample attendance data: {str(e)}')
            ) 