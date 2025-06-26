from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models      import Student, Attendance, Subject
from .serializers import StudentSerializer, AttendanceSerializer, SubjectSerializer
from datetime import date

class StudentViewSet(viewsets.ModelViewSet):
    queryset         = Student.objects.all()
    serializer_class = StudentSerializer

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_attendance(request):
    """
    POST {"student_id": "...", "subject": "..."}
    """
    sid     = request.data.get('student_id')
    subject = request.data.get('subject')
    try:
        stu = Student.objects.get(student_id=sid)
    except Student.DoesNotExist:
        return Response({'error':'Student not found'}, status=404)

    att = Attendance.objects.create(student=stu, subject=subject)
    return Response(AttendanceSerializer(att).data, status=201)

@api_view(['GET'])
def today_attendance(request):
    """
    GET /api/database/attendance/today/
    """
    qs = Attendance.objects.filter(timestamp__date=date.today())
    return Response(AttendanceSerializer(qs, many=True).data)

@api_view(['GET'])
def attendance_logs(request):
    """
    GET /api/database/attendance/logs/?date=YYYY-MM-DD
    """
    d_str = request.query_params.get('date')
    if d_str:
        try:
            d = date.fromisoformat(d_str)
        except ValueError:
            return Response({'error':'Invalid date format'}, status=400)
    else:
        d = date.today()
    qs = Attendance.objects.filter(timestamp__date=d)
    return Response(AttendanceSerializer(qs, many=True).data)

@api_view(['GET'])
def subjects_student(request):
    qs = Subject.objects.all()
    ser = SubjectSerializer(qs, many=True)
    return Response({'subjects': ser.data})

@api_view(['GET'])
def subjects_teacher(request):
    # Nếu muốn load một bộ môn khác (ví dụ khác bảng hoặc filter theo giảng viên)
    subs = Subject.objects.filter(is_for_teacher=True)
    serializer = SubjectSerializer(subs, many=True)
    return Response({'subjects': serializer.data})

class SubjectListAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]  
    queryset = Subject.objects.all().order_by('subject_name')
    serializer_class = SubjectSerializer

class StudentSubjectList(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class   = SubjectSerializer

    def get_queryset(self):
        return Subject.objects.filter(for_teacher=False).order_by('subject_name')

class TeacherSubjectList(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class   = SubjectSerializer

    def get_queryset(self):
        return Subject.objects.filter(for_teacher=True).order_by('subject_name')
