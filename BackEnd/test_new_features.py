#!/usr/bin/env python
"""
Script test các chức năng mới
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BackEnd.settings')
django.setup()

from django.contrib.auth import get_user_model
from database.models import Student, Subject, Attendance, TrainingSession
from detection.auto_training import AutoTrainingService, AttendanceWithConfidence
from users.models import User

User = get_user_model()

def test_admin_user():
    """Test user admin mặc định"""
    print("=== Test Admin User ===")
    try:
        admin_user = User.objects.get(username='admin')
        print(f"✓ Admin user tồn tại: {admin_user.username}")
        print(f"  - Email: {admin_user.email}")
        print(f"  - Role: {admin_user.role}")
        print(f"  - Is staff: {admin_user.is_staff}")
        print(f"  - Is superuser: {admin_user.is_superuser}")
        return True
    except User.DoesNotExist:
        print("✗ Admin user không tồn tại")
        return False

def test_auto_training_service():
    """Test AutoTrainingService"""
    print("\n=== Test Auto Training Service ===")
    try:
        service = AutoTrainingService()
        print("✓ AutoTrainingService khởi tạo thành công")
        
        # Test tạo folder
        folder_path = service.create_training_folder("SV001", "Nguyễn Văn A")
        print(f"✓ Tạo folder: {folder_path}")
        
        # Kiểm tra folder có tồn tại
        if folder_path.exists():
            print("✓ Folder được tạo thành công")
        else:
            print("✗ Folder không được tạo")
            
        return True
    except Exception as e:
        print(f"✗ Lỗi: {str(e)}")
        return False

def test_attendance_service():
    """Test AttendanceWithConfidence"""
    print("\n=== Test Attendance Service ===")
    try:
        service = AttendanceWithConfidence()
        print("✓ AttendanceWithConfidence khởi tạo thành công")
        
        # Kiểm tra thư mục encodings
        if service.encodings_dir.exists():
            print(f"✓ Thư mục encodings tồn tại: {service.encodings_dir}")
        else:
            print(f"✓ Thư mục encodings được tạo: {service.encodings_dir}")
            
        # Kiểm tra thư mục attendance images
        if service.attendance_images_dir.exists():
            print(f"✓ Thư mục attendance images tồn tại: {service.attendance_images_dir}")
        else:
            print(f"✓ Thư mục attendance images được tạo: {service.attendance_images_dir}")
            
        return True
    except Exception as e:
        print(f"✗ Lỗi: {str(e)}")
        return False

def test_database_models():
    """Test các model mới"""
    print("\n=== Test Database Models ===")
    try:
        # Test tạo student
        student, created = Student.objects.get_or_create(
            student_code="SV001",
            defaults={
                'name': 'Nguyễn Văn A',
                'student_class': 'CNTT-K62'
            }
        )
        if created:
            print(f"✓ Tạo student mới: {student.name}")
        else:
            print(f"✓ Student đã tồn tại: {student.name}")
        
        # Test tạo subject
        subject, created = Subject.objects.get_or_create(
            subject_name='Lập trình Python',
            defaults={
                'time': 'Thứ 2, 8:00-11:00',
                'for_teacher': False
            }
        )
        if created:
            print(f"✓ Tạo subject mới: {subject.subject_name}")
        else:
            print(f"✓ Subject đã tồn tại: {subject.subject_name}")
        
        # Test tạo attendance với confidence
        attendance = Attendance.objects.create(
            student=student,
            subject=subject.subject_name,
            status='present',
            face_detection_confidence=95.5,
            notes='Test attendance'
        )
        print(f"✓ Tạo attendance record: {attendance.id}")
        
        # Test tạo training session
        training_session = TrainingSession.objects.create(
            student=student,
            subject=subject,
            folder_path='/test/path',
            status='completed',
            images_count=5
        )
        print(f"✓ Tạo training session: {training_session.id}")
        
        return True
    except Exception as e:
        print(f"✗ Lỗi: {str(e)}")
        return False

def test_api_endpoints():
    """Test các API endpoints"""
    print("\n=== Test API Endpoints ===")
    try:
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        
        # Test endpoints tồn tại
        endpoints = [
            '/api/detection/auto-training/',
            '/api/detection/training-status/1/',
            '/api/detection/attendance-confidence/',
            '/api/database/attendance/history/',
            '/api/database/training-sessions/',
            '/api/database/attendance/summary/',
        ]
        
        for endpoint in endpoints:
            try:
                response = client.get(endpoint)
                print(f"✓ Endpoint {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"✗ Endpoint {endpoint}: {str(e)}")
        
        return True
    except Exception as e:
        print(f"✗ Lỗi: {str(e)}")
        return False

def main():
    """Chạy tất cả tests"""
    print("Bắt đầu test các chức năng mới...\n")
    
    tests = [
        test_admin_user,
        test_auto_training_service,
        test_attendance_service,
        test_database_models,
        test_api_endpoints,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} bị lỗi: {str(e)}")
    
    print(f"\n=== Kết quả ===")
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 Tất cả tests đều thành công!")
    else:
        print("⚠️  Một số tests thất bại, vui lòng kiểm tra lại.")

if __name__ == "__main__":
    main() 