from django.core.management.base import BaseCommand
from database.models import Teacher, Subject, TeacherSubject, Student, StudentSubject
from users.models import User

class Command(BaseCommand):
    help = 'Create sample data for TeacherSubject and StudentSubject relationships'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        try:
            # Get or create a teacher
            teacher, created = Teacher.objects.get_or_create(
                teacher_code='123456789012',
                defaults={
                    'name': 'Nguyễn Văn A',
                    'department': 'Công nghệ thông tin',
                    'email': 'nguyenvana@example.com',
                    'phone_number': '0123456789',
                    'address': 'Hà Nội'
                }
            )
            
            if created:
                self.stdout.write(f'Created teacher: {teacher.name}')
            else:
                self.stdout.write(f'Found existing teacher: {teacher.name}')
            
            # Get or create a subject
            subject, created = Subject.objects.get_or_create(
                subject_code='MMT2',
                defaults={
                    'subject_name': 'Mạng Máy Tính',
                    'credits': 3,
                    'description': 'Môn học về mạng máy tính'
                }
            )
            
            if created:
                self.stdout.write(f'Created subject: {subject.subject_name}')
            else:
                self.stdout.write(f'Found existing subject: {subject.subject_name}')
            
            # Create TeacherSubject relationship
            teacher_subject, created = TeacherSubject.objects.get_or_create(
                teacher=teacher,
                subject=subject,
                semester='2024-1',
                academic_year='2024-2025'
            )
            
            if created:
                self.stdout.write(f'Created TeacherSubject relationship: {teacher.name} - {subject.subject_name}')
            else:
                self.stdout.write(f'Found existing TeacherSubject relationship')
            
            # Get or create a student
            student, created = Student.objects.get_or_create(
                student_code='0123456788',
                defaults={
                    'name': 'Trần Thị B',
                    'student_class': 'CNTT-K62',
                    'email': 'tranthib@example.com',
                    'phone_number': '0987654321',
                    'address': 'Hà Nội',
                    'dayofbirth': '01/01/2000'
                }
            )
            
            if created:
                self.stdout.write(f'Created student: {student.name}')
            else:
                self.stdout.write(f'Found existing student: {student.name}')
            
            # Create StudentSubject relationship
            student_subject, created = StudentSubject.objects.get_or_create(
                student=student,
                subject=subject,
                semester='2024-1',
                academic_year='2024-2025'
            )
            
            if created:
                self.stdout.write(f'Created StudentSubject relationship: {student.name} - {subject.subject_name}')
            else:
                self.stdout.write(f'Found existing StudentSubject relationship')
            
            # Create another student for the same subject
            student2, created = Student.objects.get_or_create(
                student_code='012345678900',
                defaults={
                    'name': 'Lê Văn C',
                    'student_class': 'CNTT-K62',
                    'email': 'levanc@example.com',
                    'phone_number': '0987654322',
                    'address': 'Hà Nội',
                    'dayofbirth': '02/02/2000'
                }
            )
            
            if created:
                self.stdout.write(f'Created student: {student2.name}')
            else:
                self.stdout.write(f'Found existing student: {student2.name}')
            
            # Create StudentSubject relationship for second student
            student_subject2, created = StudentSubject.objects.get_or_create(
                student=student2,
                subject=subject,
                semester='2024-1',
                academic_year='2024-2025'
            )
            
            if created:
                self.stdout.write(f'Created StudentSubject relationship: {student2.name} - {subject.subject_name}')
            else:
                self.stdout.write(f'Found existing StudentSubject relationship')
            
            self.stdout.write(
                self.style.SUCCESS('Successfully created sample data!')
            )
            
            # Print summary
            self.stdout.write(f'\nSummary:')
            self.stdout.write(f'- Teacher: {teacher.name} ({teacher.teacher_code})')
            self.stdout.write(f'- Subject: {subject.subject_name} ({subject.subject_code})')
            self.stdout.write(f'- Students registered: {StudentSubject.objects.filter(subject=subject).count()}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating sample data: {str(e)}')
            ) 