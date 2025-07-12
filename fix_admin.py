#!/usr/bin/env python3
"""
Script kiểm tra và sửa admin user
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.append(str(Path(__file__).parent / 'BackEnd'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BackEnd.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import User

User = get_user_model()

def check_and_fix_admin():
    """Kiểm tra và sửa admin user"""
    print("=== Kiểm tra Admin User ===")
    
    try:
        # Tìm admin user
        admin_user = User.objects.get(username='admin')
        print(f"✓ Tìm thấy admin user: {admin_user.username}")
        print(f"  - Email: {admin_user.email}")
        print(f"  - Student Code: {admin_user.student_code}")
        print(f"  - Role: {admin_user.role}")
        print(f"  - Is staff: {admin_user.is_staff}")
        print(f"  - Is superuser: {admin_user.is_superuser}")
        
        # Kiểm tra student_code
        if not admin_user.student_code:
            print("⚠️  Admin user chưa có student_code, đang sửa...")
            admin_user.student_code = 'admin'
            admin_user.save()
            print("✓ Đã thêm student_code = 'admin'")
        else:
            print(f"✓ Student_code đã có: {admin_user.student_code}")
        
        # Test password
        if admin_user.check_password('Admin@1234'):
            print("✓ Password 'Admin@1234' đúng")
        else:
            print("⚠️  Password không đúng, đang reset...")
            admin_user.set_password('Admin@1234')
            admin_user.save()
            print("✓ Đã reset password thành 'Admin@1234'")
        
        print("\n=== Thông tin đăng nhập ===")
        print(f"Student Code: {admin_user.student_code}")
        print(f"Password: Admin@1234")
        print(f"URL: http://localhost:8000/api/user/login/")
        
        return True
        
    except User.DoesNotExist:
        print("✗ Không tìm thấy admin user")
        return False
    except Exception as e:
        print(f"✗ Lỗi: {str(e)}")
        return False

if __name__ == "__main__":
    check_and_fix_admin() 