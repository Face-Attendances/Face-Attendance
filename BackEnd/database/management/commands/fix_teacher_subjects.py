from django.core.management.base import BaseCommand
from database.models import Teacher, Subject, TeacherSubject, StudentSubject

class Command(BaseCommand):
    help = 'Create TeacherSubject records to link teachers with subjects'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Creating TeacherSubject data...")

        # Get existing data
        teachers = Teacher.objects.all()
        subjects = Subject.objects.all()
        student_subjects = StudentSubject.objects.all()

        self.stdout.write(f'📊 Current data:')
        self.stdout.write(f'  - Teachers: {teachers.count()}')
        self.stdout.write(f'  - Subjects: {subjects.count()}')
        self.stdout.write(f'  - StudentSubject: {student_subjects.count()}')
        self.stdout.write(f'  - TeacherSubject: {TeacherSubject.objects.count()}')

        if teachers.count() == 0:
            self.stdout.write(self.style.ERROR("❌ No teachers found!"))
            return

        if subjects.count() == 0:
            self.stdout.write(self.style.ERROR("❌ No subjects found!"))
            return

        # Create TeacherSubject records
        teacher = teachers.first()  # Use first teacher
        self.stdout.write(f'\n👨‍🏫 Using teacher: {teacher.name} ({teacher.teacher_code})')

        created_count = 0
        for subject in subjects:
            # Check if TeacherSubject already exists
            existing = TeacherSubject.objects.filter(
                teacher=teacher,
                subject=subject
            ).first()
            
            if existing:
                self.stdout.write(f'  ⚠️  Already exists: {subject.subject_name}')
                continue
            
            # Create new TeacherSubject
            ts = TeacherSubject.objects.create(
                teacher=teacher,
                subject=subject,
                semester='2024-1',
                academic_year='2024-2025'
            )
            created_count += 1
            self.stdout.write(f'  ✅ Created: {subject.subject_name} ({subject.subject_code})')

        self.stdout.write(f'\n🎉 Created {created_count} TeacherSubject records')

        # Verify the data
        self.stdout.write(f'\n🔍 Verification:')
        teacher_subjects = TeacherSubject.objects.filter(teacher=teacher)
        self.stdout.write(f'  - TeacherSubject count for {teacher.name}: {teacher_subjects.count()}')

        for ts in teacher_subjects:
            student_count = StudentSubject.objects.filter(subject=ts.subject).count()
            self.stdout.write(f'  - {ts.subject.subject_name}: {student_count} students registered')

        self.stdout.write(self.style.SUCCESS(f'\n✅ TeacherSubject creation completed!')) 