from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from .services import train_model
import os

@api_view(['POST'])
def retrain(request):
    """
    Gọi train_model với csv_path và trả về kết quả accuracy.
    """
    csv_file = request.data.get('csv_path')
    if not csv_file:
        return Response({'error': 'csv_path is required'}, status=400)
    model_path = os.path.join(settings.BASE_DIR, 'models', 'rf_model.joblib')
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    result = train_model(csv_file, model_path)
    return Response(result)
