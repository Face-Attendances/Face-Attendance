#!/usr/bin/env python3
"""
Script test trực tiếp API teachers và subjects
"""

import requests
import json

# Base URL
BASE_URL = "http://127.0.0.1:8000"

def test_teachers_api():
    """Test API teachers"""
    print("🔍 Testing teachers API directly...")
    
    try:
        # Test GET without Authorization
        response = requests.get(f"{BASE_URL}/api/database/teachers/")
        print(f"   GET /api/database/teachers/ - Status: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data)} teachers")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   Error: {str(e)}")

def test_subjects_api():
    """Test API subjects"""
    print("\n🔍 Testing subjects API directly...")
    
    try:
        # Test GET without Authorization
        response = requests.get(f"{BASE_URL}/api/database/subjects/")
        print(f"   GET /api/database/subjects/ - Status: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data)} subjects")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   Error: {str(e)}")

def test_with_auth():
    """Test với authentication"""
    print("\n🔍 Testing with authentication...")
    
    # Login first
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
                
                # Test teachers with auth
                response = requests.get(f"{BASE_URL}/api/database/teachers/", headers=headers)
                print(f"   GET teachers with auth - Status: {response.status_code}")
                
                # Test subjects with auth
                response = requests.get(f"{BASE_URL}/api/database/subjects/", headers=headers)
                print(f"   GET subjects with auth - Status: {response.status_code}")
            else:
                print("   No access token received")
        else:
            print(f"   Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"   Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Direct API Test")
    print("=" * 50)
    
    test_teachers_api()
    test_subjects_api()
    test_with_auth()
    
    print("\n✅ Test completed!") 