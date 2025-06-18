# detection/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from pathlib import Path
from .utils import FaceDetector

detector = FaceDetector()

@api_view(['POST'])
def detect_face(request):
    """
    Form-data: key 'image' chứa file upload.
    Trả về JSON: { faces: [ {x,y,w,h}, … ] }  
    """
    img = request.FILES.get('image')
    if not img:
        return Response({'error': 'No image provided'}, status=400)

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
