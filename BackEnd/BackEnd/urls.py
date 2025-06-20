from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/',        admin.site.urls),
    path('api/detection/',include('detection.urls')),
    path('api/training/', include('training.urls')),
    path('api/database/', include('database.urls')), 
    path('api/user/', include('users.urls')),
]

