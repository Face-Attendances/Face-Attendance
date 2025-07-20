import os, pickle
from pathlib import Path
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from database.models import Student
from .services import train_model

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def train_encodings(request):
    count = train_model()  # service cũ của bạn
    if count:
        return Response({'trained_faces': count})
    return Response({'error':'Không có dữ liệu để train'}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_training_status(request):
    """
    GET để kiểm tra trạng thái training.
    Trả về JSON: { trained_faces: <số lượng> }
    """
    from .services import OUTPUT_ENCODINGS
    if not OUTPUT_ENCODINGS.exists():
        return Response({'trained_faces': 0})
    
    with open(OUTPUT_ENCODINGS, 'rb') as f:
        data = pickle.load(f)
    
    return Response({'trained_faces': len(data['encodings'])})  

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_student_training(request, student_code):
    """
    Check if a specific student has training data
    """
    try:
        # Check if student exists
        student = Student.objects.get(student_code=student_code)
        
        # Check if training images exist
        training_dir = Path(settings.BASE_DIR) / 'training_data' / f"{student_code}_{student.name}"
        has_images = training_dir.exists() and any(training_dir.glob('*.jpg'))
        
        # Check if encodings exist
        from .services import OUTPUT_ENCODINGS
        has_encodings = False
        if OUTPUT_ENCODINGS.exists():
            with open(OUTPUT_ENCODINGS, 'rb') as f:
                data = pickle.load(f)
                has_encodings = student_code in data.get('names', [])
        
        return Response({
            'success': True,
            'student_code': student_code,
            'has_training': has_images and has_encodings,
            'has_images': has_images,
            'has_encodings': has_encodings
        })
        
    except Student.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Student not found'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['POST'])
@parser_classes([MultiPartParser])
@permission_classes([IsAuthenticated])
def auto_train_student(request):
    """
    Auto-train a student using captured image
    """
    try:
        student_code = request.data.get('student_code')
        image_file = request.FILES.get('image')
        attendance_id = request.data.get('attendance_id')
        
        if not student_code or not image_file:
            return Response({
                'success': False,
                'error': 'Missing student_code or image'
            }, status=400)
        
        # Get student info
        student = Student.objects.get(student_code=student_code)
        
        # Create training directory
        training_dir = Path(settings.BASE_DIR) / 'training_data' / f"{student_code}_{student.name}"
        training_dir.mkdir(parents=True, exist_ok=True)
        
        # Save training image
        image_filename = f"auto_train_{attendance_id}_{student_code}.jpg"
        image_path = training_dir / image_filename
        
        with open(image_path, 'wb') as f:
            for chunk in image_file.chunks():
                f.write(chunk)
        
        print(f"✅ Saved training image: {image_path}")
        
        # Trigger model retraining
        count = train_model()
        
        return Response({
            'success': True,
            'message': 'Auto-training completed successfully',
            'student_code': student_code,
            'image_saved': str(image_path),
            'trained_faces': count
        })
        
    except Student.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Student not found'
        }, status=404)
    except Exception as e:
        print(f"❌ Auto-training error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_training_images(request):
    user_dir = Path(settings.CAPTURED_IMAGES_DIR) / request.user.username
    images = []
    if user_dir.exists():
        for p in user_dir.iterdir():
            images.append(p.name)
    return Response({'images': images})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_training_image(request, image_name):
    user_dir = Path(settings.CAPTURED_IMAGES_DIR) / request.user.username
    image_path = user_dir / image_name
    if image_path.exists():
        image_path.unlink()
        return Response({'msg': 'Image deleted'}, status=204)
    return Response({'error': 'Image not found'}, status=404)

@api_view(['POST'])
@parser_classes([MultiPartParser])
@permission_classes([IsAuthenticated])
def upload_training_image(request):
    img = request.FILES.get('image')
    if not img:
        return Response({'error': 'No image provided'}, status=400)
    ext = Path(img.name).suffix.lower()
    if ext not in ['.jpg', '.jpeg', '.png']:
        return Response({'error': 'Only .jpg, .jpeg, and .png formats are allowed'}, status=400)

    user_dir = Path(settings.CAPTURED_IMAGES_DIR) / request.user.username
    user_dir.mkdir(parents=True, exist_ok=True)

    save_path = user_dir / img.name
    with open(save_path, 'wb') as f:
        for chunk in img.chunks():
            f.write(chunk)

    return Response({'msg': 'Image uploaded'}, status=201)