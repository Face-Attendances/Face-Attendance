from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    full_name = models.CharField(max_length=100, blank=True)
    student_id= models.CharField(max_length=20, blank=True)