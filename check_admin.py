#!/usr/bin/env python3
"""
Script kiểm tra thông tin admin user trong database
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

def check_admin_user():
    """Kiểm tra thông tin admin user"""
    print("🔍 Checking admin user in database...")
    
    try:
        # Tìm user với username admin1
        admin_user = User.objects.get(username='admin1')
        
        print(f"✅ Found admin user:")
        print(f"  Username: {admin_user.username}")
        print(f"  Full Name: {admin_user.full_name}")
        print(f"  Email: {admin_user.email}")
        print(f"  Role: {admin_user.role}")
        print(f"  Is Staff: {admin_user.is_staff}")
        print(f"  Is Superuser: {admin_user.is_superuser}")
        print(f"  Student Code: {admin_user.student_code}")
        print(f"  Teacher Code: {admin_user.teacher_code}")
        
        # Test password
        if admin_user.check_password('Admin@1234'):
            print("✅ Password is correct")
        else:
            print("❌ Password is incorrect")
            
        return admin_user
        
    except User.DoesNotExist:
        print("❌ Admin user 'admin1' not found!")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def fix_admin_user():
    """Sửa admin user nếu cần"""
    print("\n🔧 Fixing admin user...")
    
    try:
        admin_user = User.objects.get(username='admin1')
        
        # Đảm bảo role là admin
        if admin_user.role != 'admin':
            admin_user.role = 'admin'
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            print("✅ Updated admin user role to 'admin'")
        else:
            print("✅ Admin user role is already correct")
            
        return admin_user
        
    except User.DoesNotExist:
        print("❌ Admin user not found!")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    print("🚀 Admin User Check")
    print("=" * 50)
    
    # Kiểm tra admin user
    admin_user = check_admin_user()
    
    if admin_user:
        # Sửa admin user nếu cần
        fix_admin_user()
        
        print("\n✅ Admin user check completed!")
    else:
        print("\n❌ Admin user not found!") 