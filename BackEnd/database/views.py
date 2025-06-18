from django.shortcuts import render
from rest_framework import viewsets
from .models import Attendance
from .serializers import AttendanceSerializer

class AttendanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Attendance.objects.order_by('-timestamp')
    serializer_class = AttendanceSerializer
