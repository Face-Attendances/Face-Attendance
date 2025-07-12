#!/usr/bin/env python3
"""
Test script cho Face Attendance API
Kiểm tra: Login, Register, Subject, Log
"""

import requests
import json
import time
from datetime import datetime

# Cấu hình
BASE_URL = "http://localhost:8000/api"
HEADERS = {
    'Content-Type': 'application/json'
}

class APITester:
    def __init__(self):
        self.token = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, data=None):
        """Ghi log kết quả test"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
        print()
        
    def test_server_connection(self):
        """Test kết nối server"""
        try:
            response = requests.get(f"{BASE_URL}/database/students/", timeout=5)
            self.log_test("Server Connection", True, f"Server đang chạy (Status: {response.status_code})")
            return True
        except requests.exceptions.ConnectionError:
            self.log_test("Server Connection", False, "Không thể kết nối đến server. Hãy đảm bảo server đang chạy.")
            return False
        except Exception as e:
            self.log_test("Server Connection", False, f"Lỗi kết nối: {str(e)}")
            return False
    
    def test_admin_login(self):
        """Test đăng nhập admin với username"""
        try:
            # Admin login sử dụng username 'admin1'
            login_data = {
                "username": "admin1",
                "password": "Admin@1234"
            }
            
            response = requests.post(
                f"{BASE_URL}/user/login/",
                headers=HEADERS,
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'access' in data:
                    self.token = data['access']
                    self.log_test("Admin Login", True, "Đăng nhập admin thành công", {
                        'role': data.get('role', 'unknown'),
                        'access_token': data['access'][:20] + '...'
                    })
                    return True
                else:
                    self.log_test("Admin Login", False, f"Đăng nhập thất bại: {data}")
                    return False
            else:
                self.log_test("Admin Login", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Login", False, f"Lỗi: {str(e)}")
            return False
    
    def test_teacher_login(self):
        """Test đăng nhập giảng viên với teacher_code"""
        try:
            # Tạo teacher trước nếu chưa có
            teacher_data = {
                "teacher_code": "123456789012",
                "password": "teacher123",
                "password_confirm": "teacher123",
                "email": "teacher@test.com",
                "full_name": "Giảng viên Test",
                "role": "teacher"
            }
            
            # Đăng ký teacher trước
            headers_with_token = {**HEADERS, 'Authorization': f'Bearer {self.token}'}
            register_response = requests.post(
                f"{BASE_URL}/user/register/",
                headers=headers_with_token,
                json=teacher_data,
                timeout=10
            )
            
            # Đăng nhập với teacher_code
            login_data = {
                "code": "123456789012",
                "password": "teacher123"
            }
            
            response = requests.post(
                f"{BASE_URL}/user/login/",
                headers=HEADERS,
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'access' in data:
                    self.log_test("Teacher Login", True, "Đăng nhập giảng viên thành công", {
                        'role': data.get('role', 'unknown'),
                        'code': data.get('code', 'unknown')
                    })
                    return True
                else:
                    self.log_test("Teacher Login", False, f"Đăng nhập thất bại: {data}")
                    return False
            else:
                self.log_test("Teacher Login", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Teacher Login", False, f"Lỗi: {str(e)}")
            return False
    
    def test_student_login(self):
        """Test đăng nhập sinh viên với student_code"""
        try:
            # Tạo student trước nếu chưa có
            student_data = {
                "student_code": "987654321098",
                "password": "student123",
                "password_confirm": "student123",
                "email": "student@test.com",
                "full_name": "Sinh viên Test",
                "role": "student"
            }
            
            # Đăng ký student trước
            headers_with_token = {**HEADERS, 'Authorization': f'Bearer {self.token}'}
            register_response = requests.post(
                f"{BASE_URL}/user/register/",
                headers=headers_with_token,
                json=student_data,
                timeout=10
            )
            
            # Đăng nhập với student_code
            login_data = {
                "code": "987654321098",
                "password": "student123"
            }
            
            response = requests.post(
                f"{BASE_URL}/user/login/",
                headers=HEADERS,
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'access' in data:
                    self.log_test("Student Login", True, "Đăng nhập sinh viên thành công", {
                        'role': data.get('role', 'unknown'),
                        'code': data.get('code', 'unknown')
                    })
                    return True
                else:
                    self.log_test("Student Login", False, f"Đăng nhập thất bại: {data}")
                    return False
            else:
                self.log_test("Student Login", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Student Login", False, f"Lỗi: {str(e)}")
            return False
    
    def test_register_user(self):
        """Test đăng ký user mới"""
        if not self.token:
            self.log_test("Register User", False, "Chưa có token, bỏ qua test này")
            return False
            
        try:
            # Test đăng ký giảng viên
            teacher_data = {
                "teacher_code": "111111111111",
                "password": "teacher123",
                "password_confirm": "teacher123",
                "email": "teacher2@test.com",
                "full_name": "Giảng viên Test 2",
                "role": "teacher"
            }
            
            headers_with_token = {**HEADERS, 'Authorization': f'Bearer {self.token}'}
            
            response = requests.post(
                f"{BASE_URL}/user/register/",
                headers=headers_with_token,
                json=teacher_data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                if 'msg' in data and 'thành công' in data['msg']:
                    self.log_test("Register Teacher", True, "Đăng ký giảng viên thành công", {
                        'teacher_code': teacher_data['teacher_code'],
                        'role': teacher_data['role']
                    })
                else:
                    self.log_test("Register Teacher", False, f"Đăng ký thất bại: {data}")
            else:
                self.log_test("Register Teacher", False, f"HTTP {response.status_code}: {response.text}")
                
            # Test đăng ký sinh viên
            student_data = {
                "student_code": "222222222222",
                "password": "student123",
                "password_confirm": "student123",
                "email": "student2@test.com",
                "full_name": "Sinh viên Test 2",
                "role": "student"
            }
            
            response = requests.post(
                f"{BASE_URL}/user/register/",
                headers=headers_with_token,
                json=student_data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                if 'msg' in data and 'thành công' in data['msg']:
                    self.log_test("Register Student", True, "Đăng ký sinh viên thành công", {
                        'student_code': student_data['student_code'],
                        'role': student_data['role']
                    })
                else:
                    self.log_test("Register Student", False, f"Đăng ký thất bại: {data}")
            else:
                self.log_test("Register Student", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Register User", False, f"Lỗi: {str(e)}")
            return False
    
    def test_create_subject(self):
        """Test tạo môn học mới"""
        if not self.token:
            self.log_test("Create Subject", False, "Chưa có token, bỏ qua test này")
            return False
            
        try:
            subject_data = {
                "subject_name": "Lập trình Python",
                "subject_code": "CS101",
                "description": "Môn học lập trình Python cơ bản",
                "credits": 3,
                "time": "Thứ 2 08:00-11:00"
            }
            
            headers_with_token = {**HEADERS, 'Authorization': f'Bearer {self.token}'}
            
            response = requests.post(
                f"{BASE_URL}/database/subjects/create/",
                headers=headers_with_token,
                json=subject_data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                if data.get('success'):
                    self.log_test("Create Subject", True, "Tạo môn học thành công", {
                        'subject_name': subject_data['subject_name'],
                        'subject_code': subject_data['subject_code']
                    })
                    return True
                else:
                    self.log_test("Create Subject", False, f"Tạo môn học thất bại: {data.get('message', 'Unknown error')}")
                    return False
            else:
                self.log_test("Create Subject", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Create Subject", False, f"Lỗi: {str(e)}")
            return False
    
    def test_get_subjects(self):
        """Test lấy danh sách môn học"""
        try:
            response = requests.get(f"{BASE_URL}/database/subjects/", timeout=10)
            
            if response.status_code == 200:
                subjects = response.json()
                self.log_test("Get Subjects", True, f"Lấy danh sách môn học thành công ({len(subjects)} môn học)", {
                    'count': len(subjects),
                    'subjects': [s.get('subject_name', 'N/A') for s in subjects[:3]]  # Hiển thị 3 môn đầu
                })
                return True
            else:
                self.log_test("Get Subjects", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Subjects", False, f"Lỗi: {str(e)}")
            return False
    
    def test_get_attendance_log(self):
        """Test lấy log điểm danh"""
        if not self.token:
            self.log_test("Get Attendance Log", False, "Chưa có token, bỏ qua test này")
            return False
            
        try:
            headers_with_token = {**HEADERS, 'Authorization': f'Bearer {self.token}'}
            
            response = requests.get(
                f"{BASE_URL}/database/attendance/history/",
                headers=headers_with_token,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    attendance_data = data.get('data', [])
                    stats = data.get('stats', {})
                    self.log_test("Get Attendance Log", True, "Lấy log điểm danh thành công", {
                        'total_records': stats.get('total_records', 0),
                        'present_count': stats.get('present_count', 0),
                        'absent_count': stats.get('absent_count', 0),
                        'present_rate': f"{stats.get('present_rate', 0)}%",
                        'role': data.get('role', 'unknown')
                    })
                    return True
                else:
                    self.log_test("Get Attendance Log", False, f"Lấy log thất bại: {data.get('message', 'Unknown error')}")
                    return False
            else:
                self.log_test("Get Attendance Log", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Attendance Log", False, f"Lỗi: {str(e)}")
            return False
    
    def test_get_students(self):
        """Test lấy danh sách sinh viên"""
        try:
            response = requests.get(f"{BASE_URL}/database/students/", timeout=10)
            
            if response.status_code == 200:
                students = response.json()
                self.log_test("Get Students", True, f"Lấy danh sách sinh viên thành công ({len(students)} sinh viên)", {
                    'count': len(students),
                    'students': [s.get('student_code', 'N/A') for s in students[:3]]  # Hiển thị 3 sinh viên đầu
                })
                return True
            else:
                self.log_test("Get Students", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Students", False, f"Lỗi: {str(e)}")
            return False
    
    def test_get_teachers(self):
        """Test lấy danh sách giảng viên"""
        try:
            response = requests.get(f"{BASE_URL}/database/teachers/", timeout=10)
            
            if response.status_code == 200:
                teachers = response.json()
                self.log_test("Get Teachers", True, f"Lấy danh sách giảng viên thành công ({len(teachers)} giảng viên)", {
                    'count': len(teachers),
                    'teachers': [t.get('teacher_code', 'N/A') for t in teachers[:3]]  # Hiển thị 3 giảng viên đầu
                })
                return True
            else:
                self.log_test("Get Teachers", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Teachers", False, f"Lỗi: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Chạy tất cả test"""
        print("🚀 Bắt đầu test API Face Attendance System")
        print("=" * 50)
        
        # Test kết nối server
        if not self.test_server_connection():
            print("❌ Không thể kết nối server. Dừng test.")
            return
        
        # Test đăng nhập admin
        if not self.test_admin_login():
            print("❌ Không thể đăng nhập admin. Dừng test.")
            return
        
        # Test đăng nhập teacher và student
        self.test_teacher_login()
        self.test_student_login()
        
        # Test các chức năng khác
        self.test_register_user()
        self.test_create_subject()
        self.test_get_subjects()
        self.test_get_attendance_log()
        self.test_get_students()
        self.test_get_teachers()
        
        # Tổng kết
        print("=" * 50)
        print("📊 TỔNG KẾT KẾT QUẢ TEST")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Tổng số test: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Tỷ lệ thành công: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Các test thất bại:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        # Lưu kết quả vào file
        with open('test_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Kết quả chi tiết đã lưu vào: test_results.json")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests() 