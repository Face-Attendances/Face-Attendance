#!/usr/bin/env python3
"""
Script kiểm tra authentication và token
"""

import requests
import json

# API endpoints
BASE_URL = 'http://localhost:8000/api'
LOGIN_URL = f'{BASE_URL}/users/login/'
STUDENTS_URL = f'{BASE_URL}/database/students/'
TEACHERS_URL = f'{BASE_URL}/database/teachers/'
SUBJECTS_URL = f'{BASE_URL}/database/subjects/'

def test_login():
    """Test login và lấy token"""
    print("🔐 Testing login...")
    
    # Login data
    login_data = {
        'code': '123456789012',  # admin teacher_code
        'password': 'Admin@1234'
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"Access Token: {data.get('access', 'N/A')[:50]}...")
            print(f"Refresh Token: {data.get('refresh', 'N/A')[:50]}...")
            print(f"Role: {data.get('role', 'N/A')}")
            return data.get('access')
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during login: {str(e)}")
        return None

def test_api_with_token(token, endpoint, method='GET', data=None):
    """Test API với token"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        if method == 'GET':
            response = requests.get(endpoint, headers=headers)
        elif method == 'POST':
            response = requests.post(endpoint, headers=headers, json=data)
        elif method == 'PUT':
            response = requests.put(endpoint, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(endpoint, headers=headers)
        
        print(f"{method} {endpoint}")
        print(f"Status: {response.status_code}")
        
        if response.status_code in [200, 201, 204]:
            print("✅ Success!")
            if response.content:
                try:
                    result = response.json()
                    print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
                except:
                    print(f"Response: {response.text}")
        else:
            print(f"❌ Failed: {response.text}")
            
        return response.status_code
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_api_without_token(endpoint, method='GET'):
    """Test API không có token"""
    try:
        if method == 'GET':
            response = requests.get(endpoint)
        elif method == 'POST':
            response = requests.post(endpoint)
        elif method == 'DELETE':
            response = requests.delete(endpoint)
        
        print(f"{method} {endpoint} (no token)")
        print(f"Status: {response.status_code}")
        
        if response.status_code in [200, 201, 204]:
            print("✅ Success (no auth required)")
        else:
            print(f"❌ Failed: {response.text}")
            
        return response.status_code
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def main():
    print("🚀 Authentication Test")
    print("=" * 50)
    
    # Test login
    token = test_login()
    
    if not token:
        print("❌ Cannot proceed without token")
        return
    
    print("\n" + "=" * 50)
    print("🔍 Testing API endpoints...")
    
    # Test GET endpoints (should work without token)
    print("\n📋 Testing GET endpoints (no auth required):")
    test_api_without_token(STUDENTS_URL)
    test_api_without_token(TEACHERS_URL)
    test_api_without_token(SUBJECTS_URL)
    
    # Test GET endpoints with token
    print("\n🔐 Testing GET endpoints (with token):")
    test_api_with_token(token, STUDENTS_URL)
    test_api_with_token(token, TEACHERS_URL)
    test_api_with_token(token, SUBJECTS_URL)
    
    # Test POST endpoints (require auth)
    print("\n➕ Testing POST endpoints (require auth):")
    
    # Test create student
    student_data = {
        'student_code': 'TEST001',
        'name': 'Test Student',
        'student_class': 'TEST01',
        'email': 'test@example.com'
    }
    test_api_with_token(token, f'{STUDENTS_URL}create/', 'POST', student_data)
    
    # Test create teacher
    teacher_data = {
        'teacher_code': '123456789013',
        'name': 'Test Teacher',
        'department': 'Test Department',
        'email': 'teacher@example.com'
    }
    test_api_with_token(token, f'{TEACHERS_URL}create/', 'POST', teacher_data)
    
    # Test create subject
    subject_data = {
        'subject_code': 'TEST001',
        'name': 'Test Subject',
        'teacher': 1,  # Assuming teacher ID 1 exists
        'time': 'Thứ 2, 7:00-9:00'
    }
    test_api_with_token(token, f'{SUBJECTS_URL}create/', 'POST', subject_data)
    
    print("\n✅ Authentication test completed!")

if __name__ == "__main__":
    main() 