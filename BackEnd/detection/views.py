# detection/views.py

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from django.conf import settings
from pathlib import Path
from .utils import FaceDetector
from .auto_training import AutoTrainingService, AttendanceWithConfidence
from database.models import Attendance
from rest_framework import status
import numpy as np
import cv2

detector = FaceDetector()
auto_training_service = AutoTrainingService()
attendance_service = AttendanceWithConfidence()

@api_view(['POST'])
def detect_face(request):
    """
    Form-data: key 'image' chứa file upload.
    Trả về JSON: { faces: [ {x,y,w,h}, … ] }  
    """
    img = request.FILES.get('image')
    if not img:
        return Response({'error': 'No image provided'}, status=400)
    ext = Path(img.name).suffix.lower()
    if ext not in ['.jpg', '.jpeg', '.png']:
        return Response({'error': 'Only .jpg, .jpeg, and .png formats are allowed'}, status=400)

    tmp = Path(settings.MEDIA_ROOT) / img.name
    tmp.parent.mkdir(exist_ok=True)
    with open(tmp, 'wb') as f:
        for chunk in img.chunks():
            f.write(chunk)

    boxes = detector.detect(str(tmp))
    return Response({'faces': boxes})


@api_view(['POST'])
def annotate_face(request):
    """
    Form-data: key 'image'
    Trả về URL ảnh đã vẽ khung mặt.
    """
    img = request.FILES.get('image')
    if not img:
        return Response({'error': 'No image provided'}, status=400)

    uploads = Path(settings.MEDIA_ROOT) / 'uploads'
    uploads.mkdir(parents=True, exist_ok=True)
    in_path  = uploads / img.name
    out_path = uploads / f"boxed_{img.name}"

    with open(in_path, 'wb') as f:
        for c in img.chunks():
            f.write(c)

    detector.draw_faces(str(in_path), str(out_path))
    url = f"{settings.MEDIA_URL}uploads/{out_path.name}"
    return Response({'boxed_image_url': url})

@api_view(['POST'])
@parser_classes([MultiPartParser])
def process_image(request):
    # 1. Lấy file từ client (form-data key="image")
    img_file = request.FILES.get('image')
    if not img_file:
        return Response({'error': 'No image uploaded'}, status=400)

    # 2. Chuyển file bytes thành numpy array rồi decode ảnh
    file_bytes = np.frombuffer(img_file.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    # 3. Xử lý OpenCV: chuyển sang grayscale, detect face, etc.
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Dùng sẵn cascade của OpenCV
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    # 4. Chuẩn bị kết quả JSON
    results = []
    for (x, y, w, h) in faces:
        results.append({'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)})

    return Response({'faces': results})

@api_view(['POST'])
@parser_classes([MultiPartParser])
def auto_training(request):
    """
    Auto training với nhiều ảnh
    Form-data: 
    - student_id: ID của student
    - subject_id: ID của subject
    - images: List các file ảnh
    """
    try:
        student_id = request.data.get('student_id')
        subject_id = request.data.get('subject_id')
        images = request.FILES.getlist('images')
        
        if not student_id or not subject_id:
            return Response({
                'success': False,
                'message': 'Thiếu student_id hoặc subject_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not images:
            return Response({
                'success': False,
                'message': 'Không có ảnh nào được upload'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Xử lý training
        result = auto_training_service.process_training_images(student_id, subject_id, images)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_training_status(request, student_id):
    """
    Lấy trạng thái training của student
    """
    try:
        status_info = auto_training_service.get_training_status(student_id)
        if status_info:
            return Response({
                'success': True,
                'data': status_info
            })
        else:
            return Response({
                'success': False,
                'message': 'Không tìm thấy thông tin training'
            })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@parser_classes([MultiPartParser])
def process_attendance_with_confidence(request):
    """
    Xử lý attendance với confidence score
    Form-data:
    - image: File ảnh
    - subject_name: Tên môn học
    - detected_by: ID của user thực hiện (optional)
    """
    try:
        image = request.FILES.get('image')
        subject_name = request.data.get('subject_name')
        detected_by_id = request.data.get('detected_by')
        
        if not image:
            return Response({
                'success': False,
                'message': 'Không có ảnh nào được upload'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not subject_name:
            return Response({
                'success': False,
                'message': 'Thiếu tên môn học'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Lấy user nếu có
        detected_by_user = None
        if detected_by_id:
            try:
                from users.models import User
                detected_by_user = User.objects.get(id=detected_by_id)
            except User.DoesNotExist:
                pass
        
        # Xử lý attendance
        result = attendance_service.process_attendance(image, subject_name, detected_by_user)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)