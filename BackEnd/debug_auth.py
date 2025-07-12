#!/usr/bin/env python3
"""
Script debug authentication issues với teachers và subjects APIs
"""

import requests
import json

# Base URL
BASE_URL = "http://127.0.0.1:8000"

def test_api_without_auth():
    """Test API mà không có authentication"""
    print("🔍 Testing APIs without authentication...")
    
    # Test teachers API
    print("\n1. Testing teachers API:")
    try:
        response = requests.get(f"{BASE_URL}/api/database/teachers/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   Error: {str(e)}")
    
    # Test subjects API
    print("\n2. Testing subjects API:")
    try:
        response = requests.get(f"{BASE_URL}/api/database/subjects/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   Error: {str(e)}")
    
    # Test students API (for comparison)
    print("\n3. Testing students API:")
    try:
        response = requests.get(f"{BASE_URL}/api/database/students/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   Error: {str(e)}")

def test_api_with_auth():
    """Test API với authentication"""
    print("\n🔍 Testing APIs with authentication...")
    
    # Login first
    print("\n1. Logging in as admin...")
    login_data = {
        "username": "admin1",
        "password": "Admin@1234"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/api/users/login/", json=login_data)
        print(f"   Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('access')
            
            if access_token:
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                # Test teachers API with auth
                print("\n2. Testing teachers API with auth:")
                response = requests.get(f"{BASE_URL}/api/database/teachers/", headers=headers)
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
                # Test subjects API with auth
                print("\n3. Testing subjects API with auth:")
                response = requests.get(f"{BASE_URL}/api/database/subjects/", headers=headers)
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
            else:
                print("   No access token received")
        else:
            print(f"   Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"   Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Authentication Debug Test")
    print("=" * 50)
    
    test_api_without_auth()
    test_api_with_auth()
    
    print("\n✅ Debug test completed!") 