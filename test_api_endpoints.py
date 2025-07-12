import requests
import json

def test_api_endpoints():
    """Test các API endpoint chính"""
    
    base_url = "http://localhost:8000"
    
    print("=== Testing API Endpoints ===")
    
    # Test 1: Login admin
    print("\n1. Testing Admin Login...")
    login_data = {
        "code": "079205011306",
        "password": "Admin@123"
    }
    
    try:
        response = requests.post(
            f'{base_url}/api/users/login/',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✅ Admin login successful")
            token_data = response.json()
            access_token = token_data.get('access')
            print(f"   Role: {token_data.get('role')}")
            print(f"   User ID: {token_data.get('user_id')}")
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test 2: Get students
    print("\n2. Testing Get Students...")
    try:
        response = requests.get(f'{base_url}/api/database/students/')
        if response.status_code == 200:
            students = response.json()
            print(f"✅ Get students successful: {len(students)} students")
        else:
            print(f"❌ Get students failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get students error: {e}")
    
    # Test 3: Create student (with auth)
    print("\n3. Testing Create Student...")
    student_data = {
        "student_code": "123456789012",
        "name": "Test Student",
        "student_class": "CNTT-K62",
        "email": "test@example.com",
        "phone_number": "0123456789",
        "address": "Test Address"
    }
    
    try:
        response = requests.post(
            f'{base_url}/api/database/students/create/',
            json=student_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
        )
        
        if response.status_code == 201:
            print("✅ Create student successful")
        else:
            print(f"❌ Create student failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Create student error: {e}")
    
    # Test 4: Get teachers
    print("\n4. Testing Get Teachers...")
    try:
        response = requests.get(f'{base_url}/api/users/teachers/')
        if response.status_code == 200:
            teachers_data = response.json()
            teachers = teachers_data.get('data', [])
            print(f"✅ Get teachers successful: {len(teachers)} teachers")
        else:
            print(f"❌ Get teachers failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get teachers error: {e}")
    
    # Test 5: Get subjects
    print("\n5. Testing Get Subjects...")
    try:
        response = requests.get(f'{base_url}/api/database/subjects/')
        if response.status_code == 200:
            subjects = response.json()
            print(f"✅ Get subjects successful: {len(subjects)} subjects")
        else:
            print(f"❌ Get subjects failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get subjects error: {e}")
    
    # Test 6: Get attendance summary
    print("\n6. Testing Get Attendance Summary...")
    try:
        response = requests.get(f'{base_url}/api/database/attendance/summary/')
        if response.status_code == 200:
            summary_data = response.json()
            print("✅ Get attendance summary successful")
            print(f"   Total attendance: {summary_data.get('data', {}).get('total_attendance', 0)}")
        else:
            print(f"❌ Get attendance summary failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get attendance summary error: {e}")
    
    print("\n=== API Testing Completed ===")

if __name__ == "__main__":
    test_api_endpoints() 