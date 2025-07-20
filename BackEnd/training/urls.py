from django.urls import path
from .views import (
    get_training_status, upload_training_image, list_training_images, 
    train_encodings, check_student_training, auto_train_student
)

urlpatterns = [
    path('upload-image/', upload_training_image, name='upload-image'),
    path('images/',       list_training_images, name='list-images'),
    path('train/',        train_encodings,       name='train-encodings'),
    path('status/',       get_training_status,   name='get-training-status'),
    
    # Auto-training endpoints
    path('check-training/<str:student_code>/', check_student_training, name='check-student-training'),
    path('auto-train/', auto_train_student, name='auto-train-student'),
]
