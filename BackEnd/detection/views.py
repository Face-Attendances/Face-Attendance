from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import FaceDetector
from django.conf import settings
import os

detector = FaceDetector()

@api_view(['POST'])
def detect_face(request):
    """
    Nhận file ảnh upload (form-data: 'image'), trả về list bounding boxes.
    """
    img = request.FILES.get('image')
    if not img:
        return Response({'error': 'No image provided'}, status=400)

    # lưu tạm ảnh
    tmp_path = os.path.join(settings.MEDIA_ROOT, img.name)
    with open(tmp_path, 'wb+') as f:
        for chunk in img.chunks():
            f.write(chunk)

    faces = detector.detect(tmp_path)
    os.remove(tmp_path)
    return Response({'faces': faces})
