from django.core.management.base import BaseCommand
from database.models import Student, Teacher, Subject, StudentSubject, TeacherSubject

class Command(BaseCommand):
    help = 'Check data and debug student count issue'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Checking data...')
        
        # Check counts
        student_count = Student.objects.count()
        teacher_count = Teacher.objects.count()
        subject_count = Subject.objects.count()
        student_subject_count = StudentSubject.objects.count()
        teacher_subject_count = TeacherSubject.objects.count()
        
        self.stdout.write(f'📊 Counts:')
        self.stdout.write(f'  - Students: {student_count}')
        self.stdout.write(f'  - Teachers: {teacher_count}')
        self.stdout.write(f'  - Subjects: {subject_count}')
        self.stdout.write(f'  - StudentSubject: {student_subject_count}')
        self.stdout.write(f'  - TeacherSubject: {teacher_subject_count}')
        
        # Check StudentSubject details
        self.stdout.write(f'\n📚 StudentSubject details:')
        for ss in StudentSubject.objects.all():
            self.stdout.write(f'  - {ss.student.name} ({ss.student.student_code}) - {ss.subject.subject_name} ({ss.subject.subject_code}) - Semester: {ss.semester} - Year: {ss.academic_year}')
        
        # Check TeacherSubject details
        self.stdout.write(f'\n👨‍🏫 TeacherSubject details:')
        for ts in TeacherSubject.objects.all():
            self.stdout.write(f'  - {ts.teacher.name} ({ts.teacher.teacher_code}) - {ts.subject.subject_name} ({ts.subject.subject_code}) - Semester: {ts.semester} - Year: {ts.academic_year}')
        
        # Check student count for each subject
        self.stdout.write(f'\n🎯 Student count per subject:')
        for subject in Subject.objects.all():
            student_count = StudentSubject.objects.filter(subject=subject).count()
            self.stdout.write(f'  - {subject.subject_name} ({subject.subject_code}): {student_count} students')
        
        # Check if there are any TeacherSubject records
        if teacher_subject_count == 0:
            self.stdout.write(self.style.WARNING('\n⚠️  No TeacherSubject records found! This is why student count shows 0.'))
            self.stdout.write('   You need to create TeacherSubject records first.')
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ TeacherSubject records found.')) 