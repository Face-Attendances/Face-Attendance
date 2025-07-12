#!/usr/bin/env python3
"""
Test script login chỉ với code và password
"""

import requests
import json

# Cấu hình
BASE_URL = "http://localhost:8000/api"
HEADERS = {
    'Content-Type': 'application/json'
}

def test_admin_login():
    """Test đăng nhập admin với teacher_code"""
    print("🔍 Testing admin login with teacher_code...")
    
    login_data = {
        "code": "079205011306",
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
            print(f"Role: {data.get('role', 'N/A')}")
            print(f"Code: {data.get('code', 'N/A')}")
            print(f"Token: {data.get('access', 'N/A')[:20]}...")
            return data.get('access')
        else:
            print("❌ Login thất bại!")
            return None
            
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        return None

def test_invalid_code():
    """Test với code không hợp lệ"""
    print("\n🔍 Testing with invalid code...")
    
    login_data = {
        "code": "admin1",  # Không phải 12 số
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
        
        if response.status_code == 401:
            print("✅ Correctly rejected invalid code!")
        else:
            print("❌ Should have rejected invalid code!")
            
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")

if __name__ == "__main__":
    print("🚀 Testing Code-Only Login")
    print("=" * 50)
    
    # Test server connection
    try:
        response = requests.get(f"{BASE_URL}/database/students/", timeout=5)
        print(f"✅ Server đang chạy (Status: {response.status_code})")
    except:
        print("❌ Không thể kết nối server")
        exit(1)
    
    # Test admin login với teacher_code
    token = test_admin_login()
    
    # Test với code không hợp lệ
    test_invalid_code()
    
    if token:
        print(f"\n✅ Login thành công với token: {token[:20]}...")
    else:
        print(f"\n❌ Login thất bại!") 