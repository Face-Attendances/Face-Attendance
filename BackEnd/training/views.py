
import pickle
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services import train_model

@api_view(['POST'])
def train_encodings(request):
    """
    POST không cần body.
    Gọi hàm train_model và trả về số face được mã hóa.
    """
    count = train_model()
    if count:
        return Response({'trained_faces': count})
    return Response({'error': 'No faces found to train'}, status=400)
@api_view(['GET'])
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
