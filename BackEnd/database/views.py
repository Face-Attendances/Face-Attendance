from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Student, Teacher, Subject, Attendance, TrainingSession, TeacherSubject, StudentSubject
from .serializers import (
    StudentSerializer, TeacherSerializer, SubjectSerializer, 
    AttendanceSerializer, TrainingSessionSerializer, 
    TeacherSubjectSerializer, StudentSubjectSerializer
)
from users.models import User
from django.db.models import Q, Avg
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
import json

# Student views
@api_view(['GET'])
def get_students(request):
    students = Student.objects.all()
    serializer = StudentSerializer(students, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_student(request):
    serializer = StudentSerializer(data=request.data)
    if serializer.is_valid():
        student = serializer.save()
        
        # Tạo User account với mật khẩu từ ngày sinh
        if student.dayofbirth:
            # Chuyển đổi dd/mm/yyyy thành ddmmyyyy
            try:
                day, month, year = student.dayofbirth.split('/')
                password = f"{day}{month}{year}"
                
                # Tạo User account
                user = User.objects.create_user(
                    username=student.student_code,
                    email=student.email,
                    full_name=student.name,
                    role='student',
                    student_code=student.student_code,
                    teacher_code=None
                )
                user.set_password(password)
                user.save()
                
                return Response({
                    'message': 'Student created successfully',
                    'student': serializer.data,
                    'password': password
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'error': f'Error creating user account: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'error': 'dayofbirth is required to create user account'
            }, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_student(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = StudentSerializer(student, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_student(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
        student.delete()
        return Response({'message': 'Student deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

# Teacher views
@api_view(['GET'])
def get_teachers(request):
    teachers = Teacher.objects.all()
    serializer = TeacherSerializer(teachers, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_teacher(request):
    serializer = TeacherSerializer(data=request.data)
    if serializer.is_valid():
        teacher = serializer.save()
        
        # Tạo User account với mật khẩu từ ngày sinh
        if teacher.dayofbirth:
            # Chuyển đổi dd/mm/yyyy thành ddmmyyyy
            try:
                day, month, year = teacher.dayofbirth.split('/')
                password = f"{day}{month}{year}"
                
                # Tạo User account
                user = User.objects.create_user(
                    username=teacher.teacher_code,
                    email=teacher.email,
                    full_name=teacher.name,
                    role='teacher',
                    student_code=None,
                    teacher_code=teacher.teacher_code
                )
                user.set_password(password)
                user.save()
                
                return Response({
                    'message': 'Teacher created successfully',
                    'teacher': serializer.data,
                    'password': password
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'error': f'Error creating user account: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'error': 'dayofbirth is required to create user account'
            }, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_teacher(request, teacher_id):
    try:
        teacher = Teacher.objects.get(id=teacher_id)
    except Teacher.DoesNotExist:
        return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = TeacherSerializer(teacher, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_teacher(request, teacher_id):
    try:
        teacher = Teacher.objects.get(id=teacher_id)
        teacher.delete()
        return Response({'message': 'Teacher deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Teacher.DoesNotExist:
        return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)

# Subject views
@api_view(['GET'])
def get_subjects(request):
    subjects = Subject.objects.all()
    serializer = SubjectSerializer(subjects, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_subject(request):
    serializer = SubjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_subject(request, subject_id):
    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        return Response({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = SubjectSerializer(subject, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_subject(request, subject_id):
    try:
        subject = Subject.objects.get(id=subject_id)
        subject.delete()
        return Response({'message': 'Subject deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Subject.DoesNotExist:
        return Response({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)

# Teacher Subject views
@api_view(['GET'])
def get_teacher_subjects(request):
    teacher_subjects = TeacherSubject.objects.all()
    serializer = TeacherSubjectSerializer(teacher_subjects, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_teacher_subject(request):
    serializer = TeacherSubjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Student Subject views
@api_view(['GET'])
def get_student_subjects(request):
    student_subjects = StudentSubject.objects.all()
    serializer = StudentSubjectSerializer(student_subjects, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_student_subject(request):
    serializer = StudentSubjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Attendance views
@api_view(['GET'])
def get_attendance_logs(request):
    attendances = Attendance.objects.all().order_by('-timestamp')
    serializer = AttendanceSerializer(attendances, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_attendance(request):
    serializer = AttendanceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Training Session views
@api_view(['GET'])
def get_training_sessions(request):
    sessions = TrainingSession.objects.all().order_by('-created_at')
    serializer = TrainingSessionSerializer(sessions, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_training_session(request):
    serializer = TrainingSessionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Attendance Summary view
@api_view(['GET'])
def get_attendance_summary(request):
    """Get attendance summary statistics"""
    days = request.GET.get('days', 30)
    try:
        days = int(days)
    except ValueError:
        days = 30
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get attendance data for the period
    attendances = Attendance.objects.filter(
        timestamp__gte=start_date,
        timestamp__lte=end_date
    )
    
    # Calculate statistics
    total_attendance = attendances.count()
    present_count = attendances.filter(status='present').count()
    absent_count = attendances.filter(status='absent').count()
    late_count = attendances.filter(status='late').count()
    
    # Calculate percentages
    present_percentage = (present_count / total_attendance * 100) if total_attendance > 0 else 0
    absent_percentage = (absent_count / total_attendance * 100) if total_attendance > 0 else 0
    late_percentage = (late_count / total_attendance * 100) if total_attendance > 0 else 0
    
    # Get unique students and subjects
    unique_students = attendances.values('student').distinct().count()
    unique_subjects = attendances.values('subject').distinct().count()
    
    summary = {
        'total_attendance': total_attendance,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'present_percentage': round(present_percentage, 2),
        'absent_percentage': round(absent_percentage, 2),
        'late_percentage': round(late_percentage, 2),
        'unique_students': unique_students,
        'unique_subjects': unique_subjects,
        'period_days': days,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d')
    }
    
    return Response({
        'success': True,
        'data': summary
    })

# Attendance History view
@api_view(['GET'])
def get_attendance_history(request):
    """Get recent attendance history"""
    days = request.GET.get('days', 7)
    limit = request.GET.get('limit', 10)
    
    try:
        days = int(days)
        limit = int(limit)
    except ValueError:
        days = 7
        limit = 10
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get recent attendance records
    attendances = Attendance.objects.filter(
        timestamp__gte=start_date,
        timestamp__lte=end_date
    ).select_related('student', 'subject', 'teacher').order_by('-timestamp')[:limit]
    
    history_data = []
    for attendance in attendances:
        history_data.append({
            'id': attendance.id,
            'student_name': attendance.student.name,
            'student_code': attendance.student.student_code,
            'subject_name': attendance.subject.subject_name,
            'teacher_name': attendance.teacher.name if attendance.teacher else 'N/A',
            'timestamp': attendance.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'status': attendance.status,
            'confidence': attendance.face_detection_confidence,
            'image_path': attendance.image_path if attendance.image_path else None
        })
    
    return Response({
        'success': True,
        'data': history_data,
        'total_records': len(history_data),
        'period_days': days
    })

# Attendance Log Detail view
@api_view(['GET', 'DELETE'])
def get_attendance_log_detail(request, log_id):
    """Get or delete specific attendance log"""
    try:
        attendance = Attendance.objects.get(id=log_id)
    except Attendance.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Attendance record not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        data = {
            'id': attendance.id,
            'student_name': attendance.student.name,
            'student_code': attendance.student.student_code,
            'subject_name': attendance.subject.subject_name,
            'teacher_name': attendance.teacher.name if attendance.teacher else 'N/A',
            'date': attendance.timestamp.strftime('%Y-%m-%d'),
            'time': attendance.timestamp.strftime('%H:%M:%S'),
            'status': attendance.status,
            'confidence': attendance.face_detection_confidence,
            'image_path': attendance.image_path if attendance.image_path else None,
            'notes': attendance.notes
        }
        return Response({
            'success': True,
            'data': data
        })
    
    elif request.method == 'DELETE':
        attendance.delete()
        return Response({
            'success': True,
            'message': 'Attendance record deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)

# Dashboard statistics
@api_view(['GET'])
def get_dashboard_stats(request):
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_subjects = Subject.objects.count()
    total_attendance = Attendance.objects.count()
    
    # Today's attendance
    today = datetime.now().date()
    today_attendance = Attendance.objects.filter(timestamp__date=today).count()
    
    # This week's attendance
    week_start = today - timedelta(days=today.weekday())
    week_attendance = Attendance.objects.filter(timestamp__date__gte=week_start).count()
    
    stats = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_subjects': total_subjects,
        'total_attendance': total_attendance,
        'today_attendance': today_attendance,
        'week_attendance': week_attendance,
    }
    
    return Response(stats)
