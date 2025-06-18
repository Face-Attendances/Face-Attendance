
from django.urls import path
from .views import train_encodings

urlpatterns = [
    path('train/', train_encodings, name='api-train-encodings'),
]
