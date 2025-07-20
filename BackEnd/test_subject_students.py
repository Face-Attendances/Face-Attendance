import requests
import json

# Test API endpoints
BASE_URL = "http://localhost:8000/api/database"

def test_subject_students():
    """Test the subject students API"""
    print("🔍 Testing subject students API...")
    
    # First, get all subjects
    try:
        response = requests.get(f"{BASE_URL}/subjects/")
        print(f"✅ GET /subjects/ - Status: {response.status_code}")
        
        if response.status_code == 200:
            subjects = response.json()
            print(f"   Found {len(subjects)} subjects")
            
            if subjects:
                # Test with first subject
                first_subject = subjects[0]
                subject_id = first_subject['id']
                subject_name = first_subject['subject_name']
                
                print(f"\n🔍 Testing students for subject: {subject_name} (ID: {subject_id})")
                
                # Test subject students API
                students_response = requests.get(f"{BASE_URL}/subjects/{subject_id}/students/")
                print(f"✅ GET /subjects/{subject_id}/students/ - Status: {students_response.status_code}")
                
                if students_response.status_code == 200:
                    students_data = students_response.json()
                    print(f"   Response format: {type(students_data)}")
                    
                    if isinstance(students_data, dict) and 'success' in students_data:
                        print(f"   Success: {students_data['success']}")
                        students = students_data.get('data', [])
                        print(f"   Students count: {len(students)}")
                        
                        for i, student in enumerate(students[:3]):  # Show first 3 students
                            print(f"   Student {i+1}: {student.get('name', 'N/A')} ({student.get('student_code', 'N/A')})")
                    elif isinstance(students_data, list):
                        print(f"   Students count: {len(students_data)}")
                        for i, student in enumerate(students_data[:3]):  # Show first 3 students
                            print(f"   Student {i+1}: {student.get('name', 'N/A')} ({student.get('student_code', 'N/A')})")
                else:
                    print(f"   Error: {students_response.text}")
            else:
                print("   No subjects found to test")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    print()

def test_teacher_subjects():
    """Test the teacher subjects API"""
    print("🔍 Testing teacher subjects API...")
    
    try:
        response = requests.get(f"{BASE_URL}/teacher-subjects/teaching/")
        print(f"✅ GET /teacher-subjects/teaching/ - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response format: {type(data)}")
            if isinstance(data, dict) and 'success' in data:
                print(f"   Success: {data['success']}")
                subjects = data.get('data', [])
                print(f"   Subjects count: {len(subjects)}")
                
                for i, subject in enumerate(subjects[:3]):  # Show first 3 subjects
                    print(f"   Subject {i+1}: {subject.get('subject_name', 'N/A')} - Students: {subject.get('student_count', 0)}")
            elif isinstance(data, list):
                print(f"   Subjects count: {len(data)}")
                for i, subject in enumerate(data[:3]):  # Show first 3 subjects
                    print(f"   Subject {i+1}: {subject.get('subject_name', 'N/A')} - Students: {subject.get('student_count', 0)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    print()

if __name__ == "__main__":
    print("🚀 Testing Subject Students API")
    print("=" * 50)
    
    test_subject_students()
    test_teacher_subjects()
    
    print("✅ Testing completed!") 