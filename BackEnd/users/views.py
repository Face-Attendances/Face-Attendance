from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .serializers import RegisterSerializer, LoginSerializer, ForgotPasswordSerializer, UserProfileSerializer, ChangePasswordSerializer
from .models import User

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def register(request):
    ser = RegisterSerializer(data=request.data)
    if ser.is_valid():
        ser.save()
        return Response({"msg":"Đăng ký thành công"}, status=201)
    return Response(ser.errors, status=400)

@api_view(['POST'])
def login(request):
    ser = LoginSerializer(data=request.data)
    if ser.is_valid():
        return Response(ser.validated_data)
    return Response(ser.errors, status=401)

@api_view(['POST'])
def forgot_password(request):
    ser = ForgotPasswordSerializer(data=request.data)
    if ser.is_valid():
        ser.save()
        return Response({"msg":"Đã gửi link reset"}, status=200)
    return Response(ser.errors, status=400)

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile(request):
    """
    GET:   Lấy thông tin user hiện tại.
    PUT:   Cập nhật toàn bộ (tương đương PATCH với partial=False).
    PATCH: Cập nhật một số trường (partial=True).
    """
    user = request.user

    if request.method == 'GET':
        ser = UserProfileSerializer(user)
        return Response(ser.data)

    # PUT và PATCH đều dùng same serializer, chỉ khác partial flag
    partial = (request.method == 'PATCH')
    ser = UserProfileSerializer(user, data=request.data, partial=partial)
    if ser.is_valid():
        ser.save()
        return Response(ser.data)
    return Response(ser.errors, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Đổi mật khẩu cho user hiện tại"""
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        
        # Kiểm tra mật khẩu cũ
        if not user.check_password(old_password):
            return Response({
                'error': 'Mật khẩu cũ không đúng'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Đổi mật khẩu mới
        user.set_password(new_password)
        user.save()
        
        return Response({
            'message': 'Đổi mật khẩu thành công'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_teachers(request):
    """Get all teachers from User model"""
    teachers = User.objects.filter(role='teacher')
    teachers_data = []
    
    for teacher in teachers:
        teachers_data.append({
            'id': teacher.id,
            'name': teacher.full_name,
            'teacher_code': teacher.teacher_code,
            'email': teacher.email,
            'phone_number': teacher.phone_number,
            'address': teacher.address
        })
    
    return Response({
        'success': True,
        'data': teachers_data
    })