
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import models
import re
from database.models import Student, Teacher

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    student_code = serializers.CharField(write_only=True, required=False, max_length=12)
    teacher_code = serializers.CharField(write_only=True, required=False, max_length=12)
    password_confirm = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default='student')
    
    # Thêm các trường cho thông tin chi tiết
    student_class = serializers.CharField(write_only=True, required=False, max_length=50)
    department = serializers.CharField(write_only=True, required=False, max_length=100)
    phone_number = serializers.CharField(write_only=True, required=False, max_length=20)
    address = serializers.CharField(write_only=True, required=False, max_length=255)

    class Meta:
        model = User
        fields = [
            'student_code',
            'teacher_code',
            'full_name',
            'email',
            'password',
            'password_confirm',
            'role',
            'student_class',
            'department',
            'phone_number',
            'address',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        # Validate password confirmation
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError("Passwords must match.")
        
        # Validate role-specific codes
        role = data.get('role', 'student')
        if role == 'student':
            if not data.get('student_code'):
                raise serializers.ValidationError("Student code is required for student role.")
            if not re.match(r'^\d{12}$', data['student_code']):
                raise serializers.ValidationError("Student code must be exactly 12 digits.")
        elif role == 'teacher':
            if not data.get('teacher_code'):
                raise serializers.ValidationError("Teacher code is required for teacher role.")
            if not re.match(r'^\d{12}$', data['teacher_code']):
                raise serializers.ValidationError("Teacher code must be exactly 12 digits.")
        
        return data

    def create(self, validated_data):
        role = validated_data.pop('role', 'student')
        full_name = validated_data.pop('full_name')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        
        if role == 'student':
            student_code = validated_data.pop('student_code')
            username = f"{full_name.lower().replace(' ', '_')}_{student_code}"
            
            # Tạo user trong users_user table
            user = User.objects.create_user(
                username=username,
                password=password,
                full_name=full_name,
                student_code=student_code,
                email=email,
                role=role,
            )
            
            # Tạo record trong database_student table
            student = Student.objects.create(
                student_code=student_code,
                name=full_name,
                student_class=validated_data.get('student_class', ''),
                email=email,
                phone_number=validated_data.get('phone_number', ''),
                address=validated_data.get('address', '')
            )
            
        elif role == 'teacher':
            teacher_code = validated_data.pop('teacher_code')
            username = f"{full_name.lower().replace(' ', '_')}_{teacher_code}"
            
            # Tạo user trong users_user table
            user = User.objects.create_user(
                username=username,
                password=password,
                full_name=full_name,
                teacher_code=teacher_code,
                email=email,
                role=role,
                is_staff=True,
            )
            
            # Tạo record trong database_teacher table
            teacher = Teacher.objects.create(
                teacher_code=teacher_code,
                name=full_name,
                department=validated_data.get('department', ''),
                email=email,
                phone_number=validated_data.get('phone_number', ''),
                address=validated_data.get('address', '')
            )
            
        else:  # admin
            username = validated_data.pop('username', 'admin1')
            user = User.objects.create_user(
                username=username,
                password=password,
                full_name=full_name,
                email=email,
                role=role,
                is_staff=True,
                is_superuser=True,
            )
        
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=12, help_text="Student code or teacher code (12 digits)")
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        code = data.get('code')
        password = data.get('password')

        # Validate code format
        if not re.match(r'^\d{12}$', code):
            raise serializers.ValidationError("Code must be exactly 12 digits.")

        # Try to find user by student_code or teacher_code
        try:
            user = User.objects.get(
                models.Q(student_code=code) | models.Q(teacher_code=code)
            )
        except User.DoesNotExist:
            raise serializers.ValidationError("Code hoặc mật khẩu không đúng.")

        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError("Code hoặc mật khẩu không đúng.")

        # Create JWT
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'role': user.role,
            'user_id': user.id,
            'full_name': user.full_name,
            'code': code,
        }

class ForgotPasswordSerializer(serializers.Serializer):
    email_or_code = serializers.CharField()

    def validate(self, data):
        # Check if user exists by email or code
        User = get_user_model()
        try:
            user = User.objects.get(
                models.Q(email=data['email_or_code']) |
                models.Q(student_code=data['email_or_code']) |
                models.Q(teacher_code=data['email_or_code'])
            )
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        data['user'] = user
        return data

    def save(self):
        user = self.validated_data['user']
        # TODO: create reset token and send email here

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'full_name',
            'student_code',
            'teacher_code',
            'address',
            'phone_number',
            'student_class',
            'email',
            'role',
        ]
        extra_kwargs = {
            'username': {'read_only': True},
            'student_code': {'read_only': True},
            'teacher_code': {'read_only': True},
        }

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        # Kiểm tra mật khẩu mới và xác nhận mật khẩu
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Mật khẩu mới và xác nhận mật khẩu không khớp.")
        
        # Kiểm tra mật khẩu mới không được trùng với mật khẩu cũ
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError("Mật khẩu mới không được trùng với mật khẩu cũ.")
        
        return data
