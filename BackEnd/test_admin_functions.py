#!/usr/bin/env python
"""
Test script for admin functions - add, edit, delete users and subjects
"""

import os
import sys
import django
import requests
import json
from pathlib import Path

# Setup Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BackEnd.settings')
django.setup()

from django.contrib.auth import get_user_model
from database.models import Student, Teacher, Subject
from users.models import User

User = get_user_model()

# API Base URL
API_BASE_URL = 'http://localhost:8000/api'

def test_get_requests():
    """Test GET requests (should work without authentication)"""
    print("🔍 Testing GET requests (no auth required)...")
    
    endpoints = [
        f"{API_BASE_URL}/database/students/",
        f"{API_BASE_URL}/database/teachers/", 
        f"{API_BASE_URL}/database/subjects/"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint)
            print(f"  {endpoint.split('/')[-2]}: {response.status_code}")
            if response.status_code != 200:
                print(f"    Error: {response.text}")
        except Exception as e:
            print(f"  {endpoint.split('/')[-2]}: Error - {str(e)}")

def test_login():
    """Test admin login"""
    print("\n🔐 Testing admin login...")
    
    login_data = {
        "code": "079205011306",
        "password": "Admin@123"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/users/login/", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access')
            print(f"  ✅ Login successful")
            print(f"  Token: {token[:50]}...")
            return token
        else:
            print(f"  ❌ Login failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"  ❌ Login error: {str(e)}")
        return None

def test_create_student(token):
    """Test creating a student"""
    print("\n👨‍🎓 Testing create student...")
    
    import random
    # Generate valid 12-digit student code
    random_code = f"{random.randint(100000000000, 999999999999)}"
    
    student_data = {
        "student_code": random_code,
        "name": "Nguyễn Văn A",
        "student_class": "CNTT-K62",
        "dayofbirth": "01/01/2000",
        "email": f"sv{random_code}@example.com",
        "phone_number": "0123456789",
        "address": "Hà Nội"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/database/students/create/",
            json=student_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"  ✅ Student created successfully")
            print(f"  Password: {data.get('password')}")
            return data.get('student', {}).get('id')
        else:
            print(f"  ❌ Create student failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"  ❌ Create student error: {str(e)}")
        return None

def test_update_student(token, student_id):
    """Test updating a student"""
    print("\n✏️ Testing update student...")
    
    update_data = {
        "name": "Nguyễn Văn A (Updated)",
        "phone_number": "0987654321"
    }
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/database/students/{student_id}/update/",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            print(f"  ✅ Student updated successfully")
            return True
        else:
            print(f"  ❌ Update student failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Update student error: {str(e)}")
        return False

def test_delete_student(token, student_id):
    """Test deleting a student"""
    print("\n🗑️ Testing delete student...")
    
    try:
        response = requests.delete(
            f"{API_BASE_URL}/database/students/{student_id}/delete/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 204:
            print(f"  ✅ Student deleted successfully")
            return True
        else:
            print(f"  ❌ Delete student failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Delete student error: {str(e)}")
        return False

def test_create_teacher(token):
    """Test creating a teacher"""
    print("\n👨‍🏫 Testing create teacher...")
    
    import random
    # Generate valid 12-digit teacher code
    random_code = f"{random.randint(100000000000, 999999999999)}"
    
    teacher_data = {
        "teacher_code": random_code,
        "name": "Trần Thị B",
        "department": "Công nghệ thông tin",
        "dayofbirth": "15/05/1985",
        "email": f"gv{random_code}@example.com",
        "phone_number": "0123456789",
        "address": "Hà Nội"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/database/teachers/create/",
            json=teacher_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"  ✅ Teacher created successfully")
            print(f"  Password: {data.get('password')}")
            return data.get('teacher', {}).get('id')
        else:
            print(f"  ❌ Create teacher failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"  ❌ Create teacher error: {str(e)}")
        return None

def test_update_teacher(token, teacher_id):
    """Test updating a teacher"""
    print("\n✏️ Testing update teacher...")
    
    update_data = {
        "name": "Trần Thị B (Updated)",
        "phone_number": "0987654321"
    }
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/database/teachers/{teacher_id}/update/",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            print(f"  ✅ Teacher updated successfully")
            return True
        else:
            print(f"  ❌ Update teacher failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Update teacher error: {str(e)}")
        return False

def test_delete_teacher(token, teacher_id):
    """Test deleting a teacher"""
    print("\n🗑️ Testing delete teacher...")
    
    try:
        response = requests.delete(
            f"{API_BASE_URL}/database/teachers/{teacher_id}/delete/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 204:
            print(f"  ✅ Teacher deleted successfully")
            return True
        else:
            print(f"  ❌ Delete teacher failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Delete teacher error: {str(e)}")
        return False

def test_create_subject(token):
    """Test creating a subject"""
    print("\n📚 Testing create subject...")
    
    import random
    random_code = f"CS{random.randint(100, 999)}"
    
    subject_data = {
        "subject_code": random_code,
        "subject_name": "Lập trình cơ bản",
        "teacher": 1,  # Assuming teacher ID 1 exists
        "time": "Thứ 2, 8:00-11:00",
        "room": "A101",
        "credits": 3,
        "description": "Môn học cơ bản về lập trình"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/database/subjects/create/",
            json=subject_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"  ✅ Subject created successfully")
            return data.get('id')
        else:
            print(f"  ❌ Create subject failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"  ❌ Create subject error: {str(e)}")
        return None

def test_update_subject(token, subject_id):
    """Test updating a subject"""
    print("\n✏️ Testing update subject...")
    
    # Get current subject data first
    try:
        response = requests.get(f"{API_BASE_URL}/database/subjects/")
        if response.status_code == 200:
            subjects = response.json()
            current_subject = next((s for s in subjects if s['id'] == subject_id), None)
            if current_subject:
                update_data = {
                    "subject_code": current_subject.get('subject_code', ''),
                    "subject_name": "Lập trình cơ bản (Updated)",
                    "teacher": current_subject.get('teacher', 1),
                    "time": current_subject.get('time', ''),
                    "room": "A102",
                    "credits": current_subject.get('credits', 3),
                    "description": current_subject.get('description', '')
                }
            else:
                print(f"  ❌ Subject not found for update")
                return False
        else:
            print(f"  ❌ Failed to get subject data")
            return False
    except Exception as e:
        print(f"  ❌ Error getting subject data: {str(e)}")
        return False
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/database/subjects/{subject_id}/update/",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            print(f"  ✅ Subject updated successfully")
            return True
        else:
            print(f"  ❌ Update subject failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Update subject error: {str(e)}")
        return False

def test_delete_subject(token, subject_id):
    """Test deleting a subject"""
    print("\n🗑️ Testing delete subject...")
    
    try:
        response = requests.delete(
            f"{API_BASE_URL}/database/subjects/{subject_id}/delete/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 204:
            print(f"  ✅ Subject deleted successfully")
            return True
        else:
            print(f"  ❌ Delete subject failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Delete subject error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Admin Functions Test")
    print("=" * 50)
    
    # Test GET requests (no auth required)
    test_get_requests()
    
    # Test login
    token = test_login()
    if not token:
        print("\n❌ Cannot proceed without valid token")
        return
    
    # Test Student CRUD operations
    print("\n" + "=" * 50)
    print("👨‍🎓 STUDENT MANAGEMENT TESTS")
    print("=" * 50)
    
    student_id = test_create_student(token)
    if student_id:
        test_update_student(token, student_id)
        test_delete_student(token, student_id)
    
    # Test Teacher CRUD operations
    print("\n" + "=" * 50)
    print("👨‍🏫 TEACHER MANAGEMENT TESTS")
    print("=" * 50)
    
    teacher_id = test_create_teacher(token)
    if teacher_id:
        test_update_teacher(token, teacher_id)
        test_delete_teacher(token, teacher_id)
    
    # Test Subject CRUD operations
    print("\n" + "=" * 50)
    print("📚 SUBJECT MANAGEMENT TESTS")
    print("=" * 50)
    
    subject_id = test_create_subject(token)
    if subject_id:
        test_update_subject(token, subject_id)
        test_delete_subject(token, subject_id)
    
    print("\n" + "=" * 50)
    print("✅ Admin functions test completed!")
    print("=" * 50)

if __name__ == "__main__":
    main() 