from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from users.views import profile

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/',     include('users.urls')),
    path('api/database/', include('database.urls')),
    path('api/training/', include('training.urls')),
    path('api/detection/',include('detection.urls')),
    # Add missing auth endpoints that frontend expects
    path('api/auth/user/', profile, name='auth-user'),
    path('api/auth/profile/', profile, name='auth-profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])