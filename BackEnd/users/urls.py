from django.urls import path
from .views import register, login, forgot_password, profile, get_teachers, change_password

urlpatterns = [
    path('register/',        register,        name='api-register'),
    path('login/',           login,           name='api-login'),
    path('forgot-password/', forgot_password, name='api-forgot-password'),
    path('profile/',         profile,         name='api-profile'),
    path('teachers/',        get_teachers,    name='api-teachers'),
    path('change-password/', change_password, name='api-change-password'),
]
