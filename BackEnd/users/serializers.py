
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import models

User = get_user_model()

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    student_code     = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = [
            'student_code',
            'full_name',
            'email',
            'password',
            'password_confirm',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        # so sánh hai mật khẩu
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError("Passwords must match.")
        return data

    def create(self, validated_data):
        # lấy về từng biến
        student_code = validated_data.pop('student_code')
        full_name    = validated_data.pop('full_name')
        email        = validated_data.pop('email')
        password     = validated_data.pop('password')

        # sinh username ví dụ: nguyen_vana_SV001
        username = f"{full_name.lower().replace(' ', '_')}_{student_code}"

        # tạo user, gán luôn quyền admin
        user = User.objects.create_user(
            username    = username,
            password    = password,
            full_name   = full_name,
            student_code= student_code,
            email       = email,
        )
        # gán role admin
        user.is_staff     = True
        user.is_superuser = True
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        from django.contrib.auth import authenticate
        user = authenticate(**data)
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        refresh = RefreshToken.for_user(user)
        return {
            'status': 'success',
            'user_id': user.id,
            'refresh': str(refresh),
            'access':  str(refresh.access_token),
        }

class ForgotPasswordSerializer(serializers.Serializer):
    email_or_id = serializers.CharField()

    def validate(self, data):
        # kiểm tra tồn tại user theo email hoặc student_id
        User = get_user_model()
        try:
            user = User.objects.get(
                models.Q(email=data['email_or_id'])|
                models.Q(student_id=data['email_or_id'])
            )
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        data['user'] = user
        return data

    def save(self):
        user = self.validated_data['user']
        # TODO: tạo token reset và gửi email ở đây

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = [
            'username',
            'full_name',
            'student_code',
            'address',
            'phone_number',
            'student_class',
            'email',
        ]
        extra_kwargs = {
            'username':    {'read_only': True},
            'student_code':{'read_only': True},  
        }
