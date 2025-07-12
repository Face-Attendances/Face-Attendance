#!/usr/bin/env python3
"""
Script sửa admin user có teacher_code và test login
"""

import os
import sys
import django

# Thêm đường dẫn BackEnd vào sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'BackEnd'))

# Thiết lập Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BackEnd.settings')
django.setup()

from users.models import User

def fix_admin_teacher_code():
    """Sửa admin user có teacher_code"""
    print("🔧 Fixing admin user with teacher_code...")
    
    try:
        admin_user = User.objects.get(username='079205011306')
        
        # Thêm teacher_code cho admin
        admin_user.teacher_code = '079205011306'
        admin_user.role = 'admin'  # Đảm bảo role vẫn là admin
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        
        print("✅ Updated admin user:")
        print(f"  Username: {admin_user.username}")
        print(f"  Teacher Code: {admin_user.teacher_code}")
        print(f"  Role: {admin_user.role}")
        print(f"  Is Staff: {admin_user.is_staff}")
        print(f"  Is Superuser: {admin_user.is_superuser}")
        
        return admin_user
        
    except User.DoesNotExist:
        print("❌ Admin user '079205011306' not found!")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_admin_login_methods():
    """Test các cách login của admin"""
    import requests
    import json
    
    BASE_URL = "http://localhost:8000/api"
    HEADERS = {'Content-Type': 'application/json'}
    
    print("\n🧪 Testing admin login methods...")
    
    # Test 1: Login với username
    print("\n1️⃣ Testing login with username:")
    login_data = {
        "username": "079205011306",
        "password": "Admin@123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user/login/", headers=HEADERS, json=login_data, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success! Token: {data.get('access', 'N/A')[:20]}...")
            print(f"   Role: {data.get('role', 'N/A')}")
            print(f"   Code: {data.get('code', 'N/A')}")
        else:
            print(f"   ❌ Failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 2: Login với teacher_code
    print("\n2️⃣ Testing login with teacher_code:")
    login_data = {
        "code": "079205011306",
        "password": "Admin@1234"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user/login/", headers=HEADERS, json=login_data, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success! Token: {data.get('access', 'N/A')[:20]}...")
            print(f"   Role: {data.get('role', 'N/A')}")
            print(f"   Code: {data.get('code', 'N/A')}")
        else:
            print(f"   ❌ Failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Admin Teacher Code Fix & Test")
    print("=" * 50)
    
    # Sửa admin user
    admin_user = fix_admin_teacher_code()
    
    if admin_user:
        # Test login
        test_admin_login_methods()
        print("\n✅ Admin user fix and test completed!")
    else:
        print("\n❌ Failed to fix admin user!") 