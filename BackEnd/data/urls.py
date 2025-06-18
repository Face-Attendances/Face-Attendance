from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='data-index'),
    # thêm các route khác ở đây
]
