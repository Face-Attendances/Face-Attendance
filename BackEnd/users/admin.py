from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.text import slugify

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    full_name        = serializers.CharField(write_only=True, max_length=100)
    student_code     = serializers.CharField(write_only=True, max_length=20)
    email            = serializers.EmailField(write_only=True)
    password         = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    role             = serializers.ChoiceField(
        choices=User.ROLE_CHOICES,
        default='student',
        write_only=True,
        required=False
    )

    class Meta:
        model = User
        fields = [
            'full_name', 'student_code', 'email',
            'password', 'password_confirm', 'role'
        ]

    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError("Mật khẩu xác nhận không khớp.")
        return data

    def create(self, validated_data):
        full_name    = validated_data.pop('full_name')
        student_code = validated_data.pop('student_code')
        email        = validated_data.pop('email')
        password     = validated_data.pop('password')
        role         = validated_data.pop('role', 'student')

        base_username = slugify(full_name)
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}-{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.full_name    = full_name
        user.student_code = student_code
        user.role         = role
        if role == 'admin':
            user.is_staff     = True
            user.is_superuser = True
        elif role == 'teacher':
            user.is_staff     = True
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    student_code = serializers.CharField(max_length=20)
    password     = serializers.CharField(write_only=True)

    def validate(self, data):
        student_code = data.get('student_code')
        password     = data.get('password')
        try:
            user = User.objects.get(student_code=student_code)
        except User.DoesNotExist:
            raise serializers.ValidationError("MSSV hoặc mật khẩu không đúng.")
        if not user.check_password(password):
            raise serializers.ValidationError("MSSV hoặc mật khẩu không đúng.")
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access':  str(refresh.access_token),
            'role':    user.role,
        }

class ProfileSerializer(serializers.ModelSerializer):
    full_name    = serializers.CharField(required=False)
    email        = serializers.EmailField(required=False)
    password     = serializers.CharField(write_only=True, required=False)
    password_confirm = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password', 'password_confirm']

    def validate(self, data):
        pwd = data.get('password')
        confirm = data.get('password_confirm')
        if pwd or confirm:
            if pwd != confirm:
                raise serializers.ValidationError("Mật khẩu xác nhận không khớp.")
        return data

    def update(self, instance, validated_data):
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.email     = validated_data.get('email', instance.email)
        pwd = validated_data.get('password')
        if pwd:
            instance.set_password(pwd)
        instance.save()
        return instance
