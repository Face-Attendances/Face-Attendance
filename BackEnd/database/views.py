from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models      import Student, Attendance
from .serializers import StudentSerializer, AttendanceSerializer
from datetime import date

class StudentViewSet(viewsets.ModelViewSet):
    queryset         = Student.objects.all()
    serializer_class = StudentSerializer

@api_view(['POST'])
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