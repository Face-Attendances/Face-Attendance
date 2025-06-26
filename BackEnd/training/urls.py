from django.urls import path
from .views import get_training_status, upload_training_image, list_training_images, train_encodings

urlpatterns = [
    path('upload-image/', upload_training_image, name='upload-image'),
    path('images/',       list_training_images, name='list-images'),
    path('train/',        train_encodings,       name='train-encodings'),
    path('status/',       get_training_status,   name='get-training-status'),

]
