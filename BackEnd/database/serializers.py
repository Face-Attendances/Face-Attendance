from rest_framework import serializers
from .models import Student, Attendance, Subject

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Student
        fields = ['id','student_id','name','student_class']

class AttendanceSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    class Meta:
        model  = Attendance
        fields = ['id','student','subject','timestamp']

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'time']