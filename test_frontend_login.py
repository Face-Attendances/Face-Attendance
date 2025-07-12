#!/usr/bin/env python3
"""
Test script để kiểm tra login với các trường hợp khác nhau
"""

import requests
import json

# Cấu hình
BASE_URL = "http://localhost:8000/api"
HEADERS = {
    'Content-Type': 'application/json'
}

def test_valid_admin_login():
    """Test login admin hợp lệ"""
    print("🔍 Testing valid admin login...")
    
    login_data = {
        "code": "079205011306",
        "password": "Admin@1234"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user/login/", headers=HEADERS, json=login_data, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login thành công!")
            print(f"Role: {data.get('role', 'N/A')}")
            print(f"Code: {data.get('code', 'N/A')}")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_invalid_code_format():
    """Test với code không đúng format"""
    print("\n🔍 Testing invalid code format...")
    
    login_data = {
        "code": "admin1",  # Không phải 12 số
        "password": "Admin@1234"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user/login/", headers=HEADERS, json=login_data, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            data = response.json()
            print(f"✅ Correctly rejected: {data.get('non_field_errors', ['Unknown error'])[0]}")
            return True
        else:
            print(f"❌ Should have rejected invalid format")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_wrong_password():
    """Test với mật khẩu sai"""
    print("\n🔍 Testing wrong password...")
    
    login_data = {
        "code": "079205011306",
        "password": "WrongPassword"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user/login/", headers=HEADERS, json=login_data, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            data = response.json()
            print(f"✅ Correctly rejected: {data.get('non_field_errors', ['Unknown error'])[0]}")
            return True
        else:
            print(f"❌ Should have rejected wrong password")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_nonexistent_code():
    """Test với code không tồn tại"""
    print("\n🔍 Testing nonexistent code...")
    
    login_data = {
        "code": "123456789012",  # Code 12 số nhưng không tồn tại
        "password": "Admin@1234"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user/login/", headers=HEADERS, json=login_data, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            data = response.json()
            print(f"✅ Correctly rejected: {data.get('non_field_errors', ['Unknown error'])[0]}")
            return True
        else:
            print(f"❌ Should have rejected nonexistent code")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Login Logic")
    print("=" * 50)
    
    # Test server connection
    try:
        response = requests.get(f"{BASE_URL}/database/students/", timeout=5)
        print(f"✅ Server đang chạy (Status: {response.status_code})")
    except:
        print("❌ Không thể kết nối server")
        exit(1)
    
    # Run all tests
    tests = [
        test_valid_admin_login,
        test_invalid_code_format,
        test_wrong_password,
        test_nonexistent_code
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{len(tests)} passed")
    
    if passed == len(tests):
        print("✅ All tests passed! Login logic is working correctly.")
    else:
        print("❌ Some tests failed. Check the logic.") 