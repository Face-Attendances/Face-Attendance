from django.core.management.base import BaseCommand
from database.models import Student, Subject, StudentSubject
from users.models import User
from datetime import datetime

class Command(BaseCommand):
    help = 'Create sample student subject registrations'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample student subject registrations...')
        
        try:
            # Get existing students and subjects
            students = Student.objects.all()
            subjects = Subject.objects.all()
            
            if not students.exists():
                self.stdout.write(self.style.WARNING('No students found. Please create students first.'))
                return
                
            if not subjects.exists():
                self.stdout.write(self.style.WARNING('No subjects found. Please create subjects first.'))
                return
            
            # Create sample registrations
            registrations_data = [
                {
                    'student': students[0] if students.exists() else None,
                    'subject': subjects[0] if subjects.exists() else None,
                    'semester': '2024-1',
                    'academic_year': '2024-2025'
                },
                {
                    'student': students[0] if students.exists() else None,
                    'subject': subjects[1] if len(subjects) > 1 else subjects[0],
                    'semester': '2024-1',
                    'academic_year': '2024-2025'
                }
            ]
            
            # Add more registrations if we have more students
            if len(students) > 1:
                registrations_data.append({
                    'student': students[1],
                    'subject': subjects[0] if subjects.exists() else None,
                    'semester': '2024-1',
                    'academic_year': '2024-2025'
                })
                
                if len(subjects) > 1:
                    registrations_data.append({
                        'student': students[1],
                        'subject': subjects[1],
                        'semester': '2024-1',
                        'academic_year': '2024-2025'
                    })
            
            created_count = 0
            for reg_data in registrations_data:
                if reg_data['student'] and reg_data['subject']:
                    student_subject, created = StudentSubject.objects.get_or_create(
                        student=reg_data['student'],
                        subject=reg_data['subject'],
                        semester=reg_data['semester'],
                        academic_year=reg_data['academic_year']
                    )
                    if created:
                        self.stdout.write(f'Created registration: {student_subject.student.name} - {student_subject.subject.subject_name}')
                        created_count += 1
                    else:
                        self.stdout.write(f'Registration already exists: {student_subject.student.name} - {student_subject.subject.subject_name}')
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {created_count} student subject registrations!')
            )
            
            # Print summary
            total_students = Student.objects.count()
            total_subjects = Subject.objects.count()
            total_registrations = StudentSubject.objects.count()
            
            self.stdout.write(f'\nSummary:')
            self.stdout.write(f'- Total students: {total_students}')
            self.stdout.write(f'- Total subjects: {total_subjects}')
            self.stdout.write(f'- Total registrations: {total_registrations}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating student subject registrations: {str(e)}')
            ) 