# detection/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('detect/', views.detect_face, name='detect_face'),
    path('annotate/', views.annotate_face, name='annotate_face'),
    path('process/', views.process_image, name='process_image'),
    path('auto-training/', views.auto_training, name='auto_training'),
    path('training-status/<int:student_id>/', views.get_training_status, name='get_training_status'),
    path('attendance-confidence/', views.process_attendance_with_confidence, name='process_attendance_with_confidence'),
]
