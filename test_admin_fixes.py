#!/usr/bin/env python3
import requests
import json

# Test admin credentials
admin_creds = {'code': '123456789012', 'password': 'admin123'}
BASE_URL = 'http://localhost:8000/api'

print("Testing Admin Page Fixes:")
print("=" * 40)

# Login
response = requests.post(f'{BASE_URL}/users/login/', json=admin_creds)
if response.status_code == 200:
    token = response.json()['access']
    headers = {'Authorization': f'Bearer {token}'}
    
    print("✅ Admin login successful")
    
    # Test profile
    profile = requests.get(f'{BASE_URL}/users/profile/', headers=headers)
    print(f"👤 Profile: {profile.status_code}")
    
    # Test teachers endpoint (for overview.js)
    teachers = requests.get(f'{BASE_URL}/users/teachers/', headers=headers)
    print(f"👨‍🏫 Teachers: {teachers.status_code}")
    if teachers.status_code == 200:
        data = teachers.json()
        if isinstance(data, dict) and 'data' in data:
            print(f"   Found {len(data['data'])} teachers")
        else:
            print(f"   Found {len(data)} teachers")
    
    # Test dashboard data
    students = requests.get(f'{BASE_URL}/database/students/', headers=headers)
    print(f"👥 Students: {students.status_code}")
    
    subjects = requests.get(f'{BASE_URL}/database/subjects/', headers=headers)
    print(f"📚 Subjects: {subjects.status_code}")
    
    attendance_log = requests.get(f'{BASE_URL}/database/attendance/log/', headers=headers)
    print(f"📊 Attendance log: {attendance_log.status_code}")
    
else:
    print(f"❌ Admin login failed: {response.status_code}")

print(f"\n✅ All admin tests completed!") 