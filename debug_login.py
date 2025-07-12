#!/usr/bin/env python3
"""
Script debug để kiểm tra chi tiết lỗi login
"""

import requests
import json

# Cấu hình
BASE_URL = "http://localhost:8000/api"
HEADERS = {
    'Content-Type': 'application/json'
}

def debug_login_request():
    """Debug login request giống như frontend"""
    print("🔍 Debugging login request...")
    
    # Test với admin code
    login_data = {
        "code": "079205011306",
        "password": "Admin@1234"
    }
    
    print(f"Request URL: {BASE_URL}/user/login/")
    print(f"Request Headers: {HEADERS}")
    print(f"Request Body: {json.dumps(login_data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/user/login/", headers=HEADERS, json=login_data, timeout=10)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Login thành công!")
            print(f"Access Token: {data.get('access', 'N/A')[:50]}...")
            print(f"Role: {data.get('role', 'N/A')}")
            print(f"Code: {data.get('code', 'N/A')}")
        else:
            print("\n❌ Login thất bại!")
            try:
                error_data = response.json()
                print(f"Error Details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw Error: {response.text}")
                
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def test_server_status():
    """Kiểm tra trạng thái server"""
    print("🔍 Testing server status...")
    
    try:
        # Test basic endpoint
        response = requests.get(f"{BASE_URL}/database/students/", timeout=5)
        print(f"Students endpoint: {response.status_code}")
        
        # Test login endpoint (GET should return 405 Method Not Allowed)
        response = requests.get(f"{BASE_URL}/user/login/", timeout=5)
        print(f"Login endpoint (GET): {response.status_code}")
        
    except Exception as e:
        print(f"❌ Server error: {str(e)}")

def test_different_formats():
    """Test các format khác nhau"""
    print("\n🔍 Testing different request formats...")
    
    test_cases = [
        {
            "name": "Correct format",
            "data": {"code": "079205011306", "password": "Admin@1234"}
        },
        {
            "name": "With extra fields",
            "data": {"code": "079205011306", "password": "Admin@1234", "extra": "field"}
        },
        {
            "name": "String numbers",
            "data": {"code": "079205011306", "password": "Admin@1234"}
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        try:
            response = requests.post(f"{BASE_URL}/user/login/", headers=HEADERS, json=test_case['data'], timeout=10)
            print(f"Status: {response.status_code}")
            if response.status_code != 200:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Exception: {str(e)}")

if __name__ == "__main__":
    print("🚀 Login Debug Tool")
    print("=" * 50)
    
    # Test server status
    test_server_status()
    
    # Debug login request
    debug_login_request()
    
    # Test different formats
    test_different_formats() 