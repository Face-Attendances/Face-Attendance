from django.urls import path
from .views import register, login, forgot_password

urlpatterns = [
    path('register/',        register,        name='api-register'),
    path('login/',           login,           name='api-login'),
    path('forgot-password/', forgot_password, name='api-forgot-password'),
]
