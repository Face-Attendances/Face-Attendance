import requests
import json

def test_user_creation():
    """Test tạo user với các role khác nhau"""
    
    # Test data cho student
    student_data = {
        "student_code": "123456789012",
        "full_name": "Nguyen Van A",
        "email": "student1@test.com",
        "password": "password123",
        "password_confirm": "password123",
        "role": "student",
        "student_class": "CNTT-K62",
        "phone_number": "0123456789",
        "address": "Ha Noi"
    }
    
    # Test data cho teacher
    teacher_data = {
        "teacher_code": "987654321098",
        "full_name": "Tran Thi B",
        "email": "teacher1@test.com",
        "password": "password123",
        "password_confirm": "password123",
        "role": "teacher",
        "department": "Computer Science",
        "phone_number": "0987654321",
        "address": "Ho Chi Minh"
    }
    
    print("=== Testing Student Registration ===")
    try:
        response = requests.post(
            'http://localhost:8000/api/users/register/',
            json=student_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Student registration successful!")
        else:
            print("❌ Student registration failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n=== Testing Teacher Registration ===")
    try:
        response = requests.post(
            'http://localhost:8000/api/users/register/',
            json=teacher_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Teacher registration successful!")
        else:
            print("❌ Teacher registration failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n=== Testing Login ===")
    try:
        login_data = {
            "code": "123456789012",
            "password": "password123"
        }
        
        response = requests.post(
            'http://localhost:8000/api/users/login/',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
        else:
            print("❌ Login failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n=== Testing Admin Login ===")
    try:
        login_data = {
            "code": "079205011306",
            "password": "Admin@123"
        }
        response = requests.post(
            'http://localhost:8000/api/users/login/',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 200:
            print("✅ Admin login successful!")
        else:
            print("❌ Admin login failed!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_user_creation() 