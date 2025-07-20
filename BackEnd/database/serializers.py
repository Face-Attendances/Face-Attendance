from rest_framework import serializers
from .models import Student, Teacher, Subject, Attendance, TrainingSession, TeacherSubject, StudentSubject
from users.models import User

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class TeacherSubjectSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)
    subject_name = serializers.CharField(source='subject.subject_name', read_only=True)
    
    class Meta:
        model = TeacherSubject
        fields = '__all__'

class StudentSubjectSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    subject_name = serializers.CharField(source='subject.subject_name', read_only=True)
    subject_code = serializers.CharField(source='subject.subject_code', read_only=True)
    credits = serializers.IntegerField(source='subject.credits', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    room = serializers.CharField(default='Chưa cập nhật', read_only=True)
    time = serializers.CharField(default='Chưa cập nhật', read_only=True)

    def get_teacher_name(self, obj):
        teacher_subject = TeacherSubject.objects.filter(
            subject=obj.subject,
            semester=obj.semester,
            academic_year=obj.academic_year
        ).first()
        return teacher_subject.teacher.name if teacher_subject else 'Chưa phân công'
    
    class Meta:
        model = StudentSubject
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    subject_name = serializers.CharField(source='subject.subject_name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)
    detected_by_name = serializers.CharField(source='detected_by.full_name', read_only=True)
    
    class Meta:
        model = Attendance
        fields = '__all__'

class TrainingSessionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    subject_name = serializers.CharField(source='subject.subject_name', read_only=True)
    
    class Meta:
        model = TrainingSession
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'email', 'role', 'student_code', 'teacher_code']