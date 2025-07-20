from django.core.management.base import BaseCommand
from database.models import Teacher, Subject, TeacherSubject, Student, StudentSubject
from users.models import User
from datetime import datetime

class Command(BaseCommand):
    help = 'Create more sample data for testing teacher subjects management'

    def handle(self, *args, **options):
        self.stdout.write('Creating more sample data...')
        
        try:
            # Create additional subjects
            subjects_data = [
                {
                    'subject_code': 'CS101',
                    'subject_name': 'Lập trình cơ bản',
                    'credits': 3,
                    'description': 'Môn học cơ bản về lập trình'
                },
                {
                    'subject_code': 'CS201',
                    'subject_name': 'Cơ sở dữ liệu',
                    'credits': 4,
                    'description': 'Môn học về cơ sở dữ liệu'
                },
                {
                    'subject_code': 'CS301',
                    'subject_name': 'Lập trình Web',
                    'credits': 3,
                    'description': 'Môn học về lập trình web'
                }
            ]
            
            created_subjects = []
            for subject_data in subjects_data:
                subject, created = Subject.objects.get_or_create(
                    subject_code=subject_data['subject_code'],
                    defaults=subject_data
                )
                created_subjects.append(subject)
                if created:
                    self.stdout.write(f'Created subject: {subject.subject_name}')
                else:
                    self.stdout.write(f'Found existing subject: {subject.subject_name}')
            
            # Create additional teachers
            teachers_data = [
                {
                    'teacher_code': '987654321098',
                    'name': 'Trần Thị D',
                    'department': 'Công nghệ thông tin',
                    'email': 'trand@example.com',
                    'phone_number': '0123456788',
                    'address': 'TP.HCM'
                },
                {
                    'teacher_code': '111111111111',
                    'name': 'Lê Văn E',
                    'department': 'Công nghệ thông tin',
                    'email': 'levane@example.com',
                    'phone_number': '0123456789',
                    'address': 'Đà Nẵng'
                }
            ]
            
            created_teachers = []
            for teacher_data in teachers_data:
                teacher, created = Teacher.objects.get_or_create(
                    teacher_code=teacher_data['teacher_code'],
                    defaults=teacher_data
                )
                created_teachers.append(teacher)
                if created:
                    self.stdout.write(f'Created teacher: {teacher.name}')
                else:
                    self.stdout.write(f'Found existing teacher: {teacher.name}')
            
            # Create TeacherSubject relationships
            teacher_subject_data = [
                {
                    'teacher': created_teachers[0] if len(created_teachers) > 0 else Teacher.objects.first(),
                    'subject': created_subjects[0] if len(created_subjects) > 0 else Subject.objects.first(),
                    'semester': '2024-1',
                    'academic_year': '2024-2025'
                },
                {
                    'teacher': created_teachers[1] if len(created_teachers) > 1 else Teacher.objects.first(),
                    'subject': created_subjects[1] if len(created_subjects) > 1 else Subject.objects.first(),
                    'semester': '2024-1',
                    'academic_year': '2024-2025'
                }
            ]
            
            for ts_data in teacher_subject_data:
                teacher_subject, created = TeacherSubject.objects.get_or_create(
                    teacher=ts_data['teacher'],
                    subject=ts_data['subject'],
                    semester=ts_data['semester'],
                    academic_year=ts_data['academic_year']
                )
                if created:
                    self.stdout.write(f'Created TeacherSubject: {teacher_subject.teacher.name} - {teacher_subject.subject.subject_name}')
                else:
                    self.stdout.write(f'Found existing TeacherSubject')
            
            # Create user accounts for new teachers
            for teacher in created_teachers:
                user, created = User.objects.get_or_create(
                    teacher_code=teacher.teacher_code,
                    defaults={
                        'username': teacher.teacher_code,
                        'full_name': teacher.name,
                        'email': teacher.email,
                        'role': 'teacher',
                        'is_staff': True
                    }
                )
                if created:
                    user.set_password('123456')
                    user.save()
                    self.stdout.write(f'Created user account for teacher: {teacher.name}')
                else:
                    self.stdout.write(f'User account already exists for teacher: {teacher.name}')
            
            self.stdout.write(
                self.style.SUCCESS('Successfully created additional sample data!')
            )
            
            # Print summary
            total_teachers = Teacher.objects.count()
            total_subjects = Subject.objects.count()
            total_teacher_subjects = TeacherSubject.objects.count()
            
            self.stdout.write(f'\nSummary:')
            self.stdout.write(f'- Total teachers: {total_teachers}')
            self.stdout.write(f'- Total subjects: {total_subjects}')
            self.stdout.write(f'- Total teacher-subject relationships: {total_teacher_subjects}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating additional sample data: {str(e)}')
            ) 