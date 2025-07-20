from django.core.management.base import BaseCommand
from database.models import Teacher, Subject, TeacherSubject

class Command(BaseCommand):
    help = 'Create sample teacher subject relationships'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample teacher subject relationships...')
        
        try:
            # Get existing teachers and subjects
            teachers = Teacher.objects.all()
            subjects = Subject.objects.all()
            
            if not teachers.exists():
                self.stdout.write(self.style.WARNING('No teachers found. Please create teachers first.'))
                return
                
            if not subjects.exists():
                self.stdout.write(self.style.WARNING('No subjects found. Please create subjects first.'))
                return
            
            # Create sample teacher-subject relationships
            teacher_subjects_data = [
                {
                    'teacher': teachers[0] if teachers.exists() else None,
                    'subject': subjects[0] if subjects.exists() else None,
                    'semester': '2024-1',
                    'academic_year': '2024-2025'
                }
            ]
            
            # Add more relationships if we have more teachers and subjects
            if len(teachers) > 0 and len(subjects) > 1:
                teacher_subjects_data.append({
                    'teacher': teachers[0],
                    'subject': subjects[1],
                    'semester': '2024-1',
                    'academic_year': '2024-2025'
                })
            
            if len(teachers) > 0 and len(subjects) > 2:
                teacher_subjects_data.append({
                    'teacher': teachers[0],
                    'subject': subjects[2],
                    'semester': '2024-1',
                    'academic_year': '2024-2025'
                })
            
            if len(teachers) > 0 and len(subjects) > 3:
                teacher_subjects_data.append({
                    'teacher': teachers[0],
                    'subject': subjects[3],
                    'semester': '2024-1',
                    'academic_year': '2024-2025'
                })
            
            created_count = 0
            for ts_data in teacher_subjects_data:
                if ts_data['teacher'] and ts_data['subject']:
                    teacher_subject, created = TeacherSubject.objects.get_or_create(
                        teacher=ts_data['teacher'],
                        subject=ts_data['subject'],
                        semester=ts_data['semester'],
                        academic_year=ts_data['academic_year']
                    )
                    if created:
                        self.stdout.write(f'Created: {teacher_subject.teacher.name} - {teacher_subject.subject.subject_name}')
                        created_count += 1
                    else:
                        self.stdout.write(f'Already exists: {teacher_subject.teacher.name} - {teacher_subject.subject.subject_name}')
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {created_count} teacher subject relationships!')
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
                self.style.ERROR(f'Error creating teacher subject relationships: {str(e)}')
            ) 