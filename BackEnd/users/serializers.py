from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import models

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)
    class Meta:
        model  = User
        fields = ['username','password','password_confirm','full_name','student_id']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError("Passwords must match.")
        return data

    def create(self, validated):
        user = User.objects.create_user(
            username   = validated['username'],
            password   = validated['password'],
            full_name  = validated.get('full_name',''),
            student_id = validated.get('student_id',''),
        )
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
