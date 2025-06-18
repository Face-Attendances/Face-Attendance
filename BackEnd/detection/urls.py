from django.urls import path
from .views import detect_face

urlpatterns = [
    path('face/', detect_face, name='detect-face'),
]
