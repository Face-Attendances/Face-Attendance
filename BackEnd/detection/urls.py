# detection/urls.py

from django.urls import path
from .views import detect_face, annotate_face

urlpatterns = [
    path('detect/',   detect_face,   name='api-detect-face'),
    path('annotate/', annotate_face, name='api-annotate-face'),
]
