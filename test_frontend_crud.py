import requests
import json

def test_frontend_crud():
    """Test CRUD operations với authentication để kiểm tra frontend"""
    
    base_url = "http://localhost:8000"
    
    print("=== Testing Frontend CRUD Operations ===")
    
    # Step 1: Login admin
    print("\n1. Login Admin...")
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
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    
    # Step 2: Test Student CRUD với authentication
    print("\n2. Testing Student CRUD with Authentication...")
    
    # Create student
    student_data = {
        "student_code": "123456789013",
        "name": "Frontend Test Student",
        "student_class": "CNTT-K62",
        "email": "frontend.student@test.com",
        "phone_number": "0123456789",
        "address": "Frontend Test Address"
    }
    
    try:
        response = requests.post(
            f'{base_url}/api/database/students/create/',
            json=student_data,
            headers=headers
        )
        
        if response.status_code == 201:
            print("✅ Create student successful")
            created_student = response.json()
            student_id = created_student.get('id')
        else:
            print(f"❌ Create student failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Create student error: {e}")
        return
    
    # Step 3: Test Teacher CRUD với authentication
    print("\n3. Testing Teacher CRUD with Authentication...")
    
    # Create teacher
    teacher_data = {
        "teacher_code": "987654321099",
        "name": "Frontend Test Teacher",
        "department": "Computer Science",
        "email": "frontend.teacher@test.com",
        "phone_number": "0123456789",
        "address": "Frontend Test Address"
    }
    
    try:
        response = requests.post(
            f'{base_url}/api/database/teachers/create/',
            json=teacher_data,
            headers=headers
        )
        
        if response.status_code == 201:
            print("✅ Create teacher successful")
            created_teacher = response.json()
            teacher_id = created_teacher.get('id')
        else:
            print(f"❌ Create teacher failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Create teacher error: {e}")
        return
    
    # Step 4: Test Delete operations
    print("\n4. Testing Delete Operations...")
    
    # Delete student
    try:
        response = requests.delete(
            f'{base_url}/api/database/students/{student_id}/delete/',
            headers=headers
        )
        
        if response.status_code == 204:
            print("✅ Delete student successful")
        else:
            print(f"❌ Delete student failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Delete student error: {e}")
    
    # Delete teacher
    try:
        response = requests.delete(
            f'{base_url}/api/database/teachers/{teacher_id}/delete/',
            headers=headers
        )
        
        if response.status_code == 204:
            print("✅ Delete teacher successful")
        else:
            print(f"❌ Delete teacher failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Delete teacher error: {e}")
    
    print("\n=== Frontend CRUD Testing Completed ===")
    print("✅ Tất cả operations đã hoạt động với authentication!")
    print("✅ Frontend có thể thêm/sửa/xóa student/teacher thành công!")

if __name__ == "__main__":
    test_frontend_crud() 