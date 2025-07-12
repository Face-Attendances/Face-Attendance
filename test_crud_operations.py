import requests
import json

def test_crud_operations():
    """Test CRUD operations cho students và teachers"""
    
    base_url = "http://localhost:8000"
    
    print("=== Testing CRUD Operations ===")
    
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
    
    # Step 2: Test Student CRUD
    print("\n2. Testing Student CRUD Operations...")
    
    # Create student
    student_data = {
        "student_code": "123456789012",
        "name": "Test Student 1",
        "student_class": "CNTT-K62",
        "email": "student1@test.com",
        "phone_number": "0123456789",
        "address": "Test Address 1"
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
    
    # Get students
    try:
        response = requests.get(f'{base_url}/api/database/students/')
        if response.status_code == 200:
            students = response.json()
            print(f"✅ Get students successful: {len(students)} students")
        else:
            print(f"❌ Get students failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get students error: {e}")
    
    # Update student
    update_data = {
        "student_code": "123456789012",
        "name": "Updated Test Student 1",
        "student_class": "CNTT-K63",
        "email": "updated1@test.com",
        "phone_number": "0987654321",
        "address": "Updated Address 1"
    }
    
    try:
        response = requests.put(
            f'{base_url}/api/database/students/{student_id}/update/',
            json=update_data,
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Update student successful")
        else:
            print(f"❌ Update student failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Update student error: {e}")
    
    # Step 3: Test Teacher CRUD
    print("\n3. Testing Teacher CRUD Operations...")
    
    # Create teacher
    teacher_data = {
        "teacher_code": "987654321098",
        "name": "Test Teacher 1",
        "department": "Computer Science",
        "email": "teacher1@test.com",
        "phone_number": "0123456789",
        "address": "Test Address 1"
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
    
    # Get teachers
    try:
        response = requests.get(f'{base_url}/api/database/teachers/')
        if response.status_code == 200:
            teachers = response.json()
            print(f"✅ Get teachers successful: {len(teachers)} teachers")
        else:
            print(f"❌ Get teachers failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get teachers error: {e}")
    
    # Update teacher
    update_teacher_data = {
        "teacher_code": "987654321098",
        "name": "Updated Test Teacher 1",
        "department": "Information Technology",
        "email": "updated1@test.com",
        "phone_number": "0987654321",
        "address": "Updated Address 1"
    }
    
    try:
        response = requests.put(
            f'{base_url}/api/database/teachers/{teacher_id}/update/',
            json=update_teacher_data,
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Update teacher successful")
        else:
            print(f"❌ Update teacher failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Update teacher error: {e}")
    
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
    
    print("\n=== CRUD Testing Completed ===")

if __name__ == "__main__":
    test_crud_operations() 