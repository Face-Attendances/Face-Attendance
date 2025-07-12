#!/usr/bin/env python3
"""
Test script đơn giản để kiểm tra login API
"""

import requests
import json

# Cấu hình
BASE_URL = "http://localhost:8000/api"
HEADERS = {
    'Content-Type': 'application/json'
}

def test_admin_login():
    """Test đăng nhập admin với username"""
    print("🔍 Testing admin login...")
    
    # Test với username
    login_data = {
        "username": "admin1",
        "password": "Admin@1234"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/user/login/",
            headers=HEADERS,
            json=login_data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login thành công!")
            print(f"Token: {data.get('access', 'N/A')[:20]}...")
            return True
        else:
            print("❌ Login thất bại!")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        return False

def test_admin_login_with_code():
    """Test đăng nhập admin với code (nếu có)"""
    print("\n🔍 Testing admin login with code...")
    
    # Test với code (nếu admin có code)
    login_data = {
        "code": "admin1",  # Thử dùng username làm code
        "password": "Admin@1234"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/user/login/",
            headers=HEADERS,
            json=login_data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login thành công!")
            print(f"Token: {data.get('access', 'N/A')[:20]}...")
            return True
        else:
            print("❌ Login thất bại!")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Login API")
    print("=" * 50)
    
    # Test server connection
    try:
        response = requests.get(f"{BASE_URL}/database/students/", timeout=5)
        print(f"✅ Server đang chạy (Status: {response.status_code})")
    except:
        print("❌ Không thể kết nối server")
        exit(1)
    
    # Test admin login
    test_admin_login()
    test_admin_login_with_code() 