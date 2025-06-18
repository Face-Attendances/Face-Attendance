from django.urls import path
from .views import retrain

urlpatterns = [
    path('retrain/', retrain, name='retrain'),
]
