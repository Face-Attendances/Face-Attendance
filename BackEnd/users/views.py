from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import RegisterSerializer, LoginSerializer, ForgotPasswordSerializer

@api_view(['POST'])
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
