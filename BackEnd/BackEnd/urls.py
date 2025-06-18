# BackEnd/BackEnd/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/database/', include('database.urls')),
    path('api/detection/', include('detection.urls')),
    path('api/data/', include('data.urls')),        
    path('api/training/', include('training.urls')),
]
