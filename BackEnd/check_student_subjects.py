import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BackEnd.settings')
django.setup()

from database.models import Student, StudentSubject, Subject
from users.models import User

print("🔍 Checking StudentSubject data...")

# Check all StudentSubject records
student_subjects = StudentSubject.objects.select_related('student', 'subject').all()
print(f"📊 Total StudentSubject records: {student_subjects.count()}")

if student_subjects.count() > 0:
    print("\n📚 StudentSubject details:")
    for ss in student_subjects:
        print(f"  - Student: {ss.student.name} ({ss.student.student_code})")
        print(f"    Subject: {ss.subject.subject_name} ({ss.subject.subject_code})")
        print(f"    Semester: {ss.semester}, Year: {ss.academic_year}")
        print(f"    Created: {ss.created_at}")
        print()

# Check all Students
students = Student.objects.all()
print(f"👥 Total Students: {students.count()}")

if students.count() > 0:
    print("\n👥 Student details:")
    for student in students:
        print(f"  - {student.name} ({student.student_code})")
        # Check if student has User account
        try:
            user = User.objects.get(student_code=student.student_code)
            print(f"    User account: ✅ {user.username} (Role: {user.role})")
        except User.DoesNotExist:
            print(f"    User account: ❌ Not found")
        print()

# Check all Users with student_code
users_with_student_code = User.objects.filter(student_code__isnull=False).exclude(student_code='')
print(f"🔑 Users with student_code: {users_with_student_code.count()}")

if users_with_student_code.count() > 0:
    print("\n🔑 User details:")
    for user in users_with_student_code:
        print(f"  - {user.username} ({user.email})")
        print(f"    Student code: {user.student_code}")
        print(f"    Role: {user.role}")
        # Check if student exists
        try:
            student = Student.objects.get(student_code=user.student_code)
            print(f"    Student record: ✅ {student.name}")
        except Student.DoesNotExist:
            print(f"    Student record: ❌ Not found")
        print()

print("✅ Check completed!") 