#!/usr/bin/env python3
import os
import sys
import django
import requests
import json
from datetime import datetime

# Add the BackEnd directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'BackEnd'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BackEnd.settings')
django.setup()

from django.contrib.auth import get_user_model
from database.models import Student, Subject, Teacher, StudentSubject, TeacherSubject, Attendance
from users.models import User

# Railway API configuration
RAILWAY_API_URL = "https://api.railway.app/graphql/v2"
RAILWAY_TOKEN = os.getenv('RAILWAY_TOKEN')  # Set this in your environment

# Your Railway project details
PROJECT_ID = os.getenv('RAILWAY_PROJECT_ID')  # Set this in your environment
SERVICE_ID = os.getenv('RAILWAY_SERVICE_ID')  # Set this in your environment

def get_railway_variables():
    """Get Railway environment variables"""
    query = """
    query GetVariables($projectId: String!, $serviceId: String!) {
        project(id: $projectId) {
            service(id: $serviceId) {
                variables {
                    name
                    value
                }
            }
        }
    }
    """
    
    response = requests.post(RAILWAY_API_URL, json={
        'query': query,
        'variables': {
            'projectId': PROJECT_ID,
            'serviceId': SERVICE_ID
        }
    }, headers={
        'Authorization': f'Bearer {RAILWAY_TOKEN}'
    })
    
    if response.status_code == 200:
        data = response.json()
        return {var['name']: var['value'] for var in data['data']['project']['service']['variables']}
    else:
        print(f"Error getting Railway variables: {response.status_code}")
        return None

def create_sample_data():
    """Create sample data for Railway"""
    print("🚀 Starting data import to Railway...")
    
    # 1. Create Users
    print("📝 Creating users...")
    
    # Admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@uth.edu.vn',
            'full_name': 'Administrator',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("✅ Created admin user")
    
    # Student users
    students_data = [
        {
            'username': '098765432111',
            'password': '18112005',
            'full_name': 'Ngô Thanh Tân',
            'email': '098765432111@uth.edu.vn',
            'role': 'student',
            'phone_number': '0123456789',
            'address': 'Hà Nội'
        },
        {
            'username': '098765432112',
            'password': '18112005',
            'full_name': 'Ngô Thanh Tân2',
            'email': '098765432112@uth.edu.vn',
            'role': 'student',
            'phone_number': '0123456790',
            'address': 'Hà Nội'
        },
        {
            'username': '098765432113',
            'password': '18112005',
            'full_name': 'Ngô Thanh Tân5',
            'email': '098765432113@uth.edu.vn',
            'role': 'student',
            'phone_number': '0123456791',
            'address': 'Hà Nội'
        },
        {
            'username': '098765432115',
            'password': '18112005',
            'full_name': 'Ngô Thanh Tân999',
            'email': '098765432115@uth.edu.vn',
            'role': 'student',
            'phone_number': '0123456792',
            'address': 'Hà Nội'
        }
    ]
    
    for student_data in students_data:
        user, created = User.objects.get_or_create(
            username=student_data['username'],
            defaults=student_data
        )
        if created:
            user.set_password(student_data['password'])
            user.save()
            print(f"✅ Created student user: {student_data['username']}")
    
    # Teacher users
    teachers_data = [
        {
            'username': 'GV001',
            'password': 'teacher123',
            'full_name': 'Giảng viên 1',
            'email': 'gv001@uth.edu.vn',
            'role': 'teacher',
            'phone_number': '0987654321',
            'address': 'Hà Nội'
        },
        {
            'username': 'GV002',
            'password': 'teacher123',
            'full_name': 'Giảng viên 2',
            'email': 'gv002@uth.edu.vn',
            'role': 'teacher',
            'phone_number': '0987654322',
            'address': 'Hà Nội'
        }
    ]
    
    for teacher_data in teachers_data:
        user, created = User.objects.get_or_create(
            username=teacher_data['username'],
            defaults=teacher_data
        )
        if created:
            user.set_password(teacher_data['password'])
            user.save()
            print(f"✅ Created teacher user: {teacher_data['username']}")
    
    # 2. Create Students
    print("👨‍🎓 Creating students...")
    
    students = [
        {
            'student_code': '098765432111',
            'name': 'Ngô Thanh Tân',
            'email': '098765432111@uth.edu.vn',
            'phone_number': '0123456789',
            'address': 'Hà Nội',
            'day_of_birth': '2000-01-01',
            'student_class': 'CNTT-K20'
        },
        {
            'student_code': '098765432112',
            'name': 'Ngô Thanh Tân2',
            'email': '098765432112@uth.edu.vn',
            'phone_number': '0123456790',
            'address': 'Hà Nội',
            'day_of_birth': '2000-01-02',
            'student_class': 'CNTT-K20'
        },
        {
            'student_code': '098765432113',
            'name': 'Ngô Thanh Tân5',
            'email': '098765432113@uth.edu.vn',
            'phone_number': '0123456791',
            'address': 'Hà Nội',
            'day_of_birth': '2000-01-03',
            'student_class': 'CNTT-K20'
        },
        {
            'student_code': '098765432115',
            'name': 'Ngô Thanh Tân999',
            'email': '098765432115@uth.edu.vn',
            'phone_number': '0123456792',
            'address': 'Hà Nội',
            'day_of_birth': '2000-01-04',
            'student_class': 'CNTT-K20'
        }
    ]
    
    for student_data in students:
        student, created = Student.objects.get_or_create(
            student_code=student_data['student_code'],
            defaults=student_data
        )
        if created:
            print(f"✅ Created student: {student_data['name']}")
    
    # 3. Create Teachers
    print("👨‍🏫 Creating teachers...")
    
    teachers = [
        {
            'teacher_code': 'GV001',
            'name': 'Giảng viên 1',
            'email': 'gv001@uth.edu.vn',
            'phone_number': '0987654321',
            'address': 'Hà Nội',
            'day_of_birth': '1980-01-01',
            'department': 'Khoa Công nghệ thông tin'
        },
        {
            'teacher_code': 'GV002',
            'name': 'Giảng viên 2',
            'email': 'gv002@uth.edu.vn',
            'phone_number': '0987654322',
            'address': 'Hà Nội',
            'day_of_birth': '1980-01-02',
            'department': 'Khoa Công nghệ thông tin'
        }
    ]
    
    for teacher_data in teachers:
        teacher, created = Teacher.objects.get_or_create(
            teacher_code=teacher_data['teacher_code'],
            defaults=teacher_data
        )
        if created:
            print(f"✅ Created teacher: {teacher_data['name']}")
    
    # 4. Create Subjects
    print("📚 Creating subjects...")
    
    subjects = [
        {
            'subject_code': 'CS101',
            'subject_name': 'Lập trình cơ bản',
            'credits': 3,
            'description': 'Môn học cơ bản về lập trình',
            'semester': '2024-2025-1'
        },
        {
            'subject_code': 'CS102',
            'subject_name': 'Cơ sở dữ liệu',
            'credits': 3,
            'description': 'Môn học về cơ sở dữ liệu',
            'semester': '2024-2025-1'
        },
        {
            'subject_code': 'CS103',
            'subject_name': 'Lập trình Web',
            'credits': 3,
            'description': 'Môn học về lập trình web',
            'semester': '2024-2025-1'
        },
        {
            'subject_code': 'CS104',
            'subject_name': 'Mạng máy tính',
            'credits': 3,
            'description': 'Môn học về mạng máy tính',
            'semester': '2024-2025-1'
        },
        {
            'subject_code': 'CS105',
            'subject_name': 'Hệ điều hành',
            'credits': 3,
            'description': 'Môn học về hệ điều hành',
            'semester': '2024-2025-1'
        },
        {
            'subject_code': 'CS106',
            'subject_name': 'Cấu trúc dữ liệu',
            'credits': 3,
            'description': 'Môn học về cấu trúc dữ liệu',
            'semester': '2024-2025-1'
        },
        {
            'subject_code': 'CS107',
            'subject_name': 'Thuật toán',
            'credits': 3,
            'description': 'Môn học về thuật toán',
            'semester': '2024-2025-1'
        },
        {
            'subject_code': 'CS108',
            'subject_name': 'Lập trình hướng đối tượng',
            'credits': 3,
            'description': 'Môn học về lập trình hướng đối tượng',
            'semester': '2024-2025-1'
        }
    ]
    
    for subject_data in subjects:
        subject, created = Subject.objects.get_or_create(
            subject_code=subject_data['subject_code'],
            defaults=subject_data
        )
        if created:
            print(f"✅ Created subject: {subject_data['subject_name']}")
    
    # 5. Create Student-Subject relationships
    print("🔗 Creating student-subject relationships...")
    
    # Get all students and subjects
    all_students = Student.objects.all()
    all_subjects = Subject.objects.all()
    
    # Assign subjects to students
    student_subject_data = [
        # Student 1: 098765432111
        {'student_code': '098765432111', 'subject_code': 'CS101'},
        {'student_code': '098765432111', 'subject_code': 'CS102'},
        {'student_code': '098765432111', 'subject_code': 'CS103'},
        
        # Student 2: 098765432112
        {'student_code': '098765432112', 'subject_code': 'CS101'},
        {'student_code': '098765432112', 'subject_code': 'CS104'},
        {'student_code': '098765432112', 'subject_code': 'CS105'},
        
        # Student 3: 098765432113
        {'student_code': '098765432113', 'subject_code': 'CS101'},
        {'student_code': '098765432113', 'subject_code': 'CS102'},
        
        # Student 4: 098765432115
        {'student_code': '098765432115', 'subject_code': 'CS106'},
        {'student_code': '098765432115', 'subject_code': 'CS107'},
        {'student_code': '098765432115', 'subject_code': 'CS108'},
    ]
    
    for data in student_subject_data:
        student = Student.objects.get(student_code=data['student_code'])
        subject = Subject.objects.get(subject_code=data['subject_code'])
        
        student_subject, created = StudentSubject.objects.get_or_create(
            student=student,
            subject=subject,
            defaults={
                'semester': '2024-2025-1',
                'academic_year': '2024-2025'
            }
        )
        if created:
            print(f"✅ Assigned {subject.subject_name} to {student.name}")
    
    # 6. Create Teacher-Subject relationships
    print("👨‍🏫 Creating teacher-subject relationships...")
    
    teacher_subject_data = [
        {'teacher_code': 'GV001', 'subject_code': 'CS101'},
        {'teacher_code': 'GV001', 'subject_code': 'CS102'},
        {'teacher_code': 'GV001', 'subject_code': 'CS103'},
        {'teacher_code': 'GV002', 'subject_code': 'CS104'},
        {'teacher_code': 'GV002', 'subject_code': 'CS105'},
        {'teacher_code': 'GV002', 'subject_code': 'CS106'},
    ]
    
    for data in teacher_subject_data:
        teacher = Teacher.objects.get(teacher_code=data['teacher_code'])
        subject = Subject.objects.get(subject_code=data['subject_code'])
        
        teacher_subject, created = TeacherSubject.objects.get_or_create(
            teacher=teacher,
            subject=subject,
            defaults={
                'semester': '2024-2025-1',
                'academic_year': '2024-2025'
            }
        )
        if created:
            print(f"✅ Assigned {subject.subject_name} to {teacher.name}")
    
    # 7. Create sample attendance records
    print("📊 Creating sample attendance records...")
    
    # Get some students and subjects for attendance
    student1 = Student.objects.get(student_code='098765432111')
    student2 = Student.objects.get(student_code='098765432113')
    subject1 = Subject.objects.get(subject_code='CS101')
    subject2 = Subject.objects.get(subject_code='CS102')
    
    # Create attendance records for the last few days
    attendance_data = [
        {
            'student': student1,
            'subject': subject1.subject_name,
            'status': 'present',
            'timestamp': datetime.now().replace(hour=8, minute=0, second=0, microsecond=0),
            'face_detection_confidence': 95.5
        },
        {
            'student': student1,
            'subject': subject2.subject_name,
            'status': 'present',
            'timestamp': datetime.now().replace(hour=14, minute=0, second=0, microsecond=0),
            'face_detection_confidence': 92.3
        },
        {
            'student': student2,
            'subject': subject1.subject_name,
            'status': 'late',
            'timestamp': datetime.now().replace(hour=8, minute=15, second=0, microsecond=0),
            'face_detection_confidence': 88.7
        },
        {
            'student': student2,
            'subject': subject2.subject_name,
            'status': 'present',
            'timestamp': datetime.now().replace(hour=14, minute=0, second=0, microsecond=0),
            'face_detection_confidence': 94.1
        }
    ]
    
    for data in attendance_data:
        attendance, created = Attendance.objects.get_or_create(
            student=data['student'],
            subject=data['subject'],
            timestamp=data['timestamp'],
            defaults={
                'status': data['status'],
                'face_detection_confidence': data['face_detection_confidence']
            }
        )
        if created:
            print(f"✅ Created attendance record for {data['student'].name} - {data['subject']}")
    
    print("\n🎉 Data import completed successfully!")
    print(f"📊 Summary:")
    print(f"   - Users: {User.objects.count()}")
    print(f"   - Students: {Student.objects.count()}")
    print(f"   - Teachers: {Teacher.objects.count()}")
    print(f"   - Subjects: {Subject.objects.count()}")
    print(f"   - Student-Subject relationships: {StudentSubject.objects.count()}")
    print(f"   - Teacher-Subject relationships: {TeacherSubject.objects.count()}")
    print(f"   - Attendance records: {Attendance.objects.count()}")

if __name__ == "__main__":
    create_sample_data() 