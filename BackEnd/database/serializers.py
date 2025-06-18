from django.db import models
from rest_framework import serializers
from .models import Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'user', 'timestamp', 'present']
        # hoặc fields = '__all__' nếu bạn muốn include hết
