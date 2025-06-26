import os, pickle
from pathlib import Path
from django.conf import settings
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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