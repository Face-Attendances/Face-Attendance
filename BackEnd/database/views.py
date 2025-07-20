from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
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
@permission_classes([])  # Remove authentication temporarily
def get_students(request):
    students = Student.objects.all()
    serializer = StudentSerializer(students, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([])  # Remove authentication temporarily
def create_student(request):
    serializer = StudentSerializer(data=request.data)
    if serializer.is_valid():
        student = serializer.save()
        # Tạo User account với mật khẩu từ ngày sinh
        if student.dayofbirth:
            try:
                day, month, year = student.dayofbirth.split('/')
                password = f"{day}{month}{year}"
                # Kiểm tra user đã tồn tại chưa
                if not User.objects.filter(student_code=student.student_code).exists():
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
                        'message': 'Student & user account created successfully',
                        'student': serializer.data,
                        'password': password
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        'message': 'Student created, user account already exists',
                        'student': serializer.data
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
@permission_classes([])
def update_student_by_code(request, student_code):
    try:
        student = Student.objects.get(student_code=student_code)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = StudentSerializer(student, data=request.data)
    if serializer.is_valid():
        serializer.save()
        # Cập nhật user nếu có
        try:
            user = User.objects.get(student_code=student_code)
            user.full_name = request.data.get('name', user.full_name)
            user.email = request.data.get('email', user.email)
            user.save()
        except User.DoesNotExist:
            pass
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([])
def delete_student_by_code(request, student_code):
    try:
        student = Student.objects.get(student_code=student_code)
        # Xóa user nếu có
        try:
            user = User.objects.get(student_code=student_code)
            user.delete()
        except User.DoesNotExist:
            pass
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
@permission_classes([])  # Remove authentication temporarily
def create_teacher(request):
    serializer = TeacherSerializer(data=request.data)
    if serializer.is_valid():
        try:
            teacher = serializer.save()
            # Tạo User account với mật khẩu từ ngày sinh
            if teacher.dayofbirth:
                try:
                    day, month, year = teacher.dayofbirth.split('/')
                    password = f"{day}{month}{year}"
                    # Kiểm tra user đã tồn tại chưa
                    if not User.objects.filter(teacher_code=teacher.teacher_code).exists():
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
                            'message': 'Teacher & user account created successfully',
                            'teacher': serializer.data,
                            'password': password
                        }, status=status.HTTP_201_CREATED)
                    else:
                        return Response({
                            'message': 'Teacher created, user account already exists',
                            'teacher': serializer.data
                        }, status=status.HTTP_201_CREATED)
                except Exception as e:
                    teacher.delete()
                    return Response({
                        'error': f'Error creating user account: {str(e)}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                teacher.delete()
                return Response({
                    'error': 'dayofbirth is required to create user account'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            if 'duplicate key value' in str(e):
                return Response({
                    'error': f'Teacher with this teacher code already exists: {request.data.get("teacher_code", "unknown")}'
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'error': f'Error creating teacher: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([])
def update_teacher_by_code(request, teacher_code):
    try:
        teacher = Teacher.objects.get(teacher_code=teacher_code)
    except Teacher.DoesNotExist:
        return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = TeacherSerializer(teacher, data=request.data)
    if serializer.is_valid():
        serializer.save()
        # Cập nhật user nếu có
        try:
            user = User.objects.get(teacher_code=teacher_code)
            user.full_name = request.data.get('name', user.full_name)
            user.email = request.data.get('email', user.email)
            user.save()
        except User.DoesNotExist:
            pass
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([])
def delete_teacher_by_code(request, teacher_code):
    try:
        teacher = Teacher.objects.get(teacher_code=teacher_code)
        # Xóa user nếu có
        try:
            user = User.objects.get(teacher_code=teacher_code)
            user.delete()
        except User.DoesNotExist:
            pass
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

@api_view(['GET'])
def get_subject_students(request, subject_id):
    """Get students registered for a specific subject"""
    try:
        # Check if subject exists
        subject = Subject.objects.get(id=subject_id)
        
        # Get current semester and academic year
        from datetime import datetime
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        
        # Determine current semester
        if current_month >= 8 and current_month <= 12:
            current_semester = f"{current_year}-1"
            current_academic_year = f"{current_year}-{current_year + 1}"
        else:
            current_semester = f"{current_year - 1}-2"
            current_academic_year = f"{current_year - 1}-{current_year}"
        
        # Get students registered for this subject in current semester
        student_subjects = StudentSubject.objects.filter(
            subject=subject,
            semester=current_semester,
            academic_year=current_academic_year
        ).select_related('student')
        
        print(f"🔍 Debug get_subject_students:")
        print(f"  Subject ID: {subject_id}")
        print(f"  Current semester: {current_semester}")
        print(f"  Current academic year: {current_academic_year}")
        print(f"  Found {student_subjects.count()} student registrations")
        
        students_data = []
        for ss in student_subjects:
            students_data.append({
                'id': ss.student.id,
                'student_code': ss.student.student_code,
                'name': ss.student.name,
                'student_class': ss.student.student_class,
                'email': ss.student.email,
                'phone_number': ss.student.phone_number,
                'address': ss.student.address,
                'dayofbirth': ss.student.dayofbirth,
                'registration_date': ss.created_at,
                'semester': ss.semester,
                'academic_year': ss.academic_year
            })
        
        print(f"📚 Returning {len(students_data)} students")
        
        return Response({
            'success': True,
            'data': students_data
        })
        
    except Subject.DoesNotExist:
        return Response({
            'error': 'Subject not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([])  # Remove authentication temporarily
def create_subject(request):
    serializer = SubjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([])  # Remove authentication temporarily
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
@permission_classes([])  # Remove authentication temporarily
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_teacher_teaching_subjects(request):
    """Get subjects that a specific teacher is teaching with student count"""
    user = request.user
    
    # Debug logging
    print(f"🔍 Debug get_teacher_teaching_subjects:")
    print(f"  User ID: {user.id}")
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Role: {getattr(user, 'role', 'NO_ROLE')}")
    print(f"  Teacher code: {getattr(user, 'teacher_code', 'NO_TEACHER_CODE')}")
    
    if not hasattr(user, 'role') or user.role != 'teacher':
        return Response({
            'error': f'Only teachers can access this endpoint. Current role: {getattr(user, "role", "NO_ROLE")}'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Get teacher by teacher_code
        teacher = Teacher.objects.get(teacher_code=user.teacher_code)
        
        # Get teacher subjects
        teacher_subjects = TeacherSubject.objects.filter(teacher=teacher)
        
        # Get current semester and academic year
        from datetime import datetime
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        
        # Determine current semester
        if current_month >= 8 and current_month <= 12:
            current_semester = f"{current_year}-1"
            current_academic_year = f"{current_year}-{current_year + 1}"
        else:
            current_semester = f"{current_year - 1}-2"
            current_academic_year = f"{current_year - 1}-{current_year}"
        
        subjects_data = []
        for ts in teacher_subjects:
            # Count students registered for this subject in current semester
            student_count = StudentSubject.objects.filter(
                subject=ts.subject,
                semester=current_semester,
                academic_year=current_academic_year
            ).count()
            
            subjects_data.append({
                'id': ts.subject.id,
                'subject_code': ts.subject.subject_code,
                'subject_name': ts.subject.subject_name,
                'credits': ts.subject.credits,
                'description': ts.subject.description,
                'semester': ts.semester,
                'academic_year': ts.academic_year,
                'student_count': student_count,
                'teacher_name': teacher.name
            })
        
        return Response({
            'success': True,
            'data': subjects_data
        })
        
    except Teacher.DoesNotExist:
        return Response({
            'error': 'Teacher not found',
            'teacher_code': user.teacher_code
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_teacher_subject(request):
    serializer = TeacherSubjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_teacher_subject(request, teacher_subject_id):
    """Update teacher subject relationship"""
    try:
        teacher_subject = TeacherSubject.objects.get(id=teacher_subject_id)
    except TeacherSubject.DoesNotExist:
        return Response({'error': 'Teacher subject relationship not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = TeacherSubjectSerializer(teacher_subject, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_teacher_subject(request, teacher_subject_id):
    """Delete teacher subject relationship"""
    try:
        teacher_subject = TeacherSubject.objects.get(id=teacher_subject_id)
        teacher_subject.delete()
        return Response({'message': 'Teacher subject relationship deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except TeacherSubject.DoesNotExist:
        return Response({'error': 'Teacher subject relationship not found'}, status=status.HTTP_404_NOT_FOUND)

# StudentSubject CRUD operations
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_student_subject(request, student_subject_id):
    """Update student subject relationship"""
    try:
        student_subject = StudentSubject.objects.get(id=student_subject_id)
    except StudentSubject.DoesNotExist:
        return Response({'error': 'Student subject relationship not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = StudentSubjectSerializer(student_subject, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_student_subject(request, student_subject_id):
    """Delete student subject relationship"""
    try:
        student_subject = StudentSubject.objects.get(id=student_subject_id)
        student_subject.delete()
        return Response({'message': 'Student subject relationship deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except StudentSubject.DoesNotExist:
        return Response({'error': 'Student subject relationship not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_subject_detail(request, student_subject_id):
    """Get detailed information about a specific student-subject relationship"""
    try:
        student_subject = StudentSubject.objects.get(id=student_subject_id)
        
        # Check if the current user is the student or admin
        user = request.user
        if user.role == 'student' and student_subject.student.student_code != user.student_code:
            return Response({
                'error': 'You can only view your own student-subject relationships'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Prepare response data
        data = {
            'id': student_subject.id,
            'student_id': student_subject.student.id,
            'student_code': student_subject.student.student_code,
            'student_name': student_subject.student.name,
            'subject_id': student_subject.subject.id,
            'subject_code': student_subject.subject.subject_code,
            'subject_name': student_subject.subject.subject_name,
            'credits': student_subject.subject.credits,
            'description': student_subject.subject.description,
            'semester': student_subject.semester,
            'academic_year': student_subject.academic_year,
            'registration_date': student_subject.created_at
        }
        
        return Response({
            'success': True,
            'data': data
        })
        
    except StudentSubject.DoesNotExist:
        return Response({
            'error': 'Student-subject relationship not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_teacher_subject_detail(request, teacher_subject_id):
    """Get detailed information about a specific teacher-subject relationship"""
    try:
        teacher_subject = TeacherSubject.objects.get(id=teacher_subject_id)
        
        # Check if the current user is the teacher or admin
        user = request.user
        if user.role == 'teacher' and teacher_subject.teacher.teacher_code != user.teacher_code:
            return Response({
                'error': 'You can only view your own teacher-subject relationships'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get student count for this subject
        student_count = StudentSubject.objects.filter(
            subject=teacher_subject.subject,
            semester=teacher_subject.semester,
            academic_year=teacher_subject.academic_year
        ).count()
        
        # Prepare response data
        data = {
            'id': teacher_subject.id,
            'teacher_id': teacher_subject.teacher.id,
            'teacher_code': teacher_subject.teacher.teacher_code,
            'teacher_name': teacher_subject.teacher.name,
            'subject_id': teacher_subject.subject.id,
            'subject_code': teacher_subject.subject.subject_code,
            'subject_name': teacher_subject.subject.subject_name,
            'credits': teacher_subject.subject.credits,
            'description': teacher_subject.subject.description,
            'semester': teacher_subject.semester,
            'academic_year': teacher_subject.academic_year,
            'student_count': student_count
        }
        
        return Response({
            'success': True,
            'data': data
        })
        
    except TeacherSubject.DoesNotExist:
        return Response({
            'error': 'Teacher-subject relationship not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_subjects_with_details(request):
    """Get all student-subject relationships with detailed information"""
    try:
        print("🔍 Fetching student subjects...")
        student_subjects = StudentSubject.objects.select_related('student', 'subject').all()
        print(f"📊 Found {student_subjects.count()} student subjects")
        
        data = []
        for ss in student_subjects:
            data.append({
                'id': ss.id,
                'student_id': ss.student.id,
                'student_code': ss.student.student_code,
                'student_name': ss.student.name,
                'subject_id': ss.subject.id,
                'subject_code': ss.subject.subject_code,
                'subject_name': ss.subject.subject_name,
                'credits': ss.subject.credits,
                'semester': ss.semester,
                'academic_year': ss.academic_year,
                'registration_date': ss.created_at
            })
        
        print(f"📤 Returning {len(data)} records")
        return Response({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_teacher_subjects_with_details(request):
    """Get teacher subjects with detailed information"""
    try:
        print("🔍 Fetching teacher subjects with details...")
        teacher_subjects = TeacherSubject.objects.select_related('teacher', 'subject').all()
        print(f"📊 Found {teacher_subjects.count()} teacher subjects")
        
        data = []
        for ts in teacher_subjects:
            # Count students for this subject (regardless of semester/academic_year)
            student_count = StudentSubject.objects.filter(
                subject=ts.subject
            ).count()
            
            print(f"📚 Subject: {ts.subject.subject_name} - Students: {student_count}")
            
            data.append({
                'id': ts.id,
                'teacher_id': ts.teacher.id,
                'teacher_name': ts.teacher.name,
                'teacher_code': ts.teacher.teacher_code,
                'subject_id': ts.subject.id,
                'subject_name': ts.subject.subject_name,
                'subject_code': ts.subject.subject_code,
                'semester': ts.semester,
                'academic_year': ts.academic_year,
                'student_count': student_count,
                'created_at': ts.created_at
            })
        
        return Response({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Student Subject views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_subjects(request):
    """Get all student subject registrations with detailed information"""
    try:
        student_subjects = StudentSubject.objects.select_related('student', 'subject').all()
        
        data = []
        for ss in student_subjects:
            data.append({
                'id': ss.id,
                'student_id': ss.student.id,
                'student_code': ss.student.student_code,
                'student_name': ss.student.name,
                'subject_id': ss.subject.id,
                'subject_code': ss.subject.subject_code,
                'subject_name': ss.subject.subject_name,
                'credits': ss.subject.credits,
                'description': ss.subject.description,
                'semester': ss.semester,
                'academic_year': ss.academic_year,
                'created_at': ss.created_at
            })
        
        return Response({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_student_subject(request):
    try:
        # Validate student exists
        student_id = request.data.get('student')
        if not Student.objects.filter(id=student_id).exists():
            return Response({
                'message': 'Sinh viên không tồn tại'
            }, status=status.HTTP_404_NOT_FOUND)

        # Validate subject exists
        subject_id = request.data.get('subject')
        if not Subject.objects.filter(id=subject_id).exists():
            return Response({
                'message': 'Môn học không tồn tại'
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if already registered
        if StudentSubject.objects.filter(
            student_id=student_id,
            subject_id=subject_id,
            semester=request.data.get('semester'),
            academic_year=request.data.get('academic_year')
        ).exists():
            return Response({
                'success': False,
                'message': 'Sinh viên đã đăng ký môn học này'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = StudentSubjectSerializer(data=request.data)
        if serializer.is_valid():
            registration = serializer.save()
            return Response({
                'success': True,
                'message': 'Đăng ký môn học thành công',
                'data': StudentSubjectSerializer(registration).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': 'Dữ liệu không hợp lệ',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Lỗi khi đăng ký môn học: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# Attendance views
@api_view(['GET'])
@permission_classes([])  # Remove authentication temporarily
def get_attendance_logs(request):
    """Get attendance logs - temporarily without authentication"""
    try:
        # Base queryset - return all attendance for testing
        attendances = Attendance.objects.select_related('student', 'subject', 'teacher').order_by('-timestamp')
        
        # Apply filters from request parameters
        date_filter = request.GET.get('date')
        subject_filter = request.GET.get('subject')
        student_filter = request.GET.get('student')
        
        if date_filter:
            attendances = attendances.filter(timestamp__date=date_filter)
        if subject_filter:
            attendances = attendances.filter(subject_id=subject_filter)
        if student_filter:
            attendances = attendances.filter(student_id=student_filter)
        
        # Limit results for performance
        attendances = attendances[:50]
        
        serializer = AttendanceSerializer(attendances, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_attendance(request):
    """Create new attendance record"""
    user = request.user
    data = request.data.copy()
    
    try:
        # If student_code provided, find the student
        if 'student_code' in data:
            student = Student.objects.get(student_code=data['student_code'])
            data['student'] = student.id
            del data['student_code']
        
        # If subject_id provided, use it directly
        if 'subject_id' in data:
            data['subject'] = data['subject_id']
            del data['subject_id']
        
        # Set detected_by to current user
        data['detected_by'] = user.id
        
        # Set default status if not provided
        if 'status' not in data:
            data['status'] = 'present'
        
        serializer = AttendanceSerializer(data=data)
        if serializer.is_valid():
            attendance = serializer.save()
            response_data = AttendanceSerializer(attendance).data
            return Response({
                'success': True,
                'message': 'Attendance recorded successfully',
                'data': response_data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Student.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Student not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Subject.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Subject not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error creating attendance: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
@permission_classes([IsAuthenticated])
def get_attendance_summary(request):
    """Get attendance summary statistics filtered by user role"""
    user = request.user
    days = request.GET.get('days', 30)
    student_code = request.GET.get('student_code')  # For specific student lookup
    
    try:
        days = int(days)
    except ValueError:
        days = 30
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Base queryset with date filtering
    attendances = Attendance.objects.filter(
        timestamp__gte=start_date,
        timestamp__lte=end_date
    )
    
    # Apply role-based filtering
    if user.role == 'admin':
        # Admin sees all attendance records
        pass
    elif user.role == 'teacher':
        # Teacher sees only attendance for subjects they teach
        teacher_subjects = TeacherSubject.objects.filter(
            teacher__teacher_code=user.teacher_code
        ).values_list('subject_id', flat=True)
        attendances = attendances.filter(subject_id__in=teacher_subjects)
    elif user.role == 'student':
        # Student sees only their own attendance records
        attendances = attendances.filter(student__student_code=user.student_code)
    else:
        # Unknown role - return empty queryset
        attendances = attendances.none()
    
    # If specific student_code provided (for student statistics API)
    if student_code and user.role in ['admin', 'teacher']:
        attendances = attendances.filter(student__student_code=student_code)
    
    # Calculate statistics
    total_attendance = attendances.count()
    present_count = attendances.filter(status='present').count()
    absent_count = attendances.filter(status='absent').count()
    late_count = attendances.filter(status='late').count()
    
    # Calculate today's attendance for student role
    today_attendance = 0
    if user.role == 'student':
        today = datetime.now().date()
        today_attendance = attendances.filter(timestamp__date=today).count()
    
    # Calculate percentages
    present_percentage = (present_count / total_attendance * 100) if total_attendance > 0 else 0
    absent_percentage = (absent_count / total_attendance * 100) if total_attendance > 0 else 0
    late_percentage = (late_count / total_attendance * 100) if total_attendance > 0 else 0
    
    # Calculate average confidence
    avg_confidence = attendances.aggregate(
        avg_conf=Avg('face_detection_confidence')
    )['avg_conf'] or 0
    
    # Get unique students and subjects (admin/teacher only)
    unique_students = attendances.values('student').distinct().count()
    unique_subjects = attendances.values('subject').distinct().count()
    
    summary = {
        'total_attendance': total_attendance,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'today_attendance': today_attendance,  # For student role
        'present_percentage': round(present_percentage, 2),
        'absent_percentage': round(absent_percentage, 2),
        'late_percentage': round(late_percentage, 2),
        'avg_face_detection_confidence': round(avg_confidence, 1) if avg_confidence else 0,
        'unique_students': unique_students,
        'unique_subjects': unique_subjects,
        'period_days': days,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'user_role': user.role
    }
    
    return Response(summary)

# Attendance History view
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_attendance_history(request):
    """Get recent attendance history filtered by user role"""
    user = request.user
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
    
    # Base queryset with role filtering
    attendances = Attendance.objects.filter(
        timestamp__gte=start_date,
        timestamp__lte=end_date
    ).select_related('student', 'subject', 'teacher')
    
    # Apply role-based filtering
    if user.role == 'admin':
        # Admin sees all attendance records
        pass
    elif user.role == 'teacher':
        # Teacher sees only attendance for subjects they teach
        teacher_subjects = TeacherSubject.objects.filter(
            teacher__teacher_code=user.teacher_code
        ).values_list('subject_id', flat=True)
        attendances = attendances.filter(subject_id__in=teacher_subjects)
    elif user.role == 'student':
        # Student sees only their own attendance records
        attendances = attendances.filter(student__student_code=user.student_code)
    else:
        # Unknown role - return empty queryset
        attendances = attendances.none()
    
    # Apply limit and order
    attendances = attendances.order_by('-timestamp')[:limit]
    
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
        'period_days': days,
        'user_role': user.role
    })

# Attendance Log Detail view
@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def get_attendance_log_detail(request, log_id):
    """Get or delete specific attendance log with role-based permissions"""
    try:
        attendance = Attendance.objects.select_related('student', 'subject', 'teacher').get(id=log_id)
        
        # Check permissions based on user role
        user = request.user
        has_permission = False
        
        if user.role == 'admin':
            has_permission = True
        elif user.role == 'teacher':
            # Teacher can access attendance for subjects they teach
            teacher_subjects = TeacherSubject.objects.filter(
                teacher__teacher_code=user.teacher_code
            ).values_list('subject_id', flat=True)
            has_permission = attendance.subject_id in teacher_subjects
        elif user.role == 'student':
            # Student can only access their own attendance
            has_permission = str(attendance.student.student_code) == str(user.student_code)
        
        if not has_permission:
            return Response({
                'error': 'You do not have permission to access this attendance record'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if request.method == 'DELETE':
            attendance.delete()
            return Response({
                'success': True,
                'message': 'Attendance record deleted successfully'
            })
            
        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data)
        
    except Attendance.DoesNotExist:
        return Response({
            'error': 'Attendance record not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_teacher_attendance(request):
    """Get attendance records for subjects taught by the teacher"""
    user = request.user
    if user.role != 'teacher':
        return Response({
            'error': 'Only teachers can access this endpoint'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Get subjects taught by this teacher
        teacher_subjects = TeacherSubject.objects.filter(
            teacher__teacher_code=user.teacher_code
        ).values_list('subject_id', flat=True)
        
        # Get attendance for these subjects
        attendance = Attendance.objects.filter(
            subject_id__in=teacher_subjects
        ).select_related('student', 'subject')
        
        # Apply filters if provided
        date = request.GET.get('date')
        if date:
            attendance = attendance.filter(timestamp__date=date)
            
        subject_id = request.GET.get('subject_id')
        if subject_id:
            attendance = attendance.filter(subject_id=subject_id)
            
        student_code = request.GET.get('student_code')
        if student_code:
            attendance = attendance.filter(student__student_code=student_code)
        
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Dashboard statistics
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_stats(request):
    """Get dashboard statistics filtered by user role"""
    user = request.user
    
    try:
        if user.role == 'admin':
            # Admin sees all statistics
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
            
        elif user.role == 'teacher':
            # Teacher sees only statistics for subjects they teach
            teacher_subjects = TeacherSubject.objects.filter(
                teacher__teacher_code=user.teacher_code
            ).values_list('subject_id', flat=True)
            
            # Count students registered for teacher's subjects
            total_students = StudentSubject.objects.filter(
                subject_id__in=teacher_subjects
            ).values('student').distinct().count()
            
            total_teachers = 1  # Just the current teacher
            total_subjects = len(teacher_subjects)
            
            # Attendance for teacher's subjects
            attendances = Attendance.objects.filter(subject_id__in=teacher_subjects)
            total_attendance = attendances.count()
            
            # Today's attendance for teacher's subjects
            today = datetime.now().date()
            today_attendance = attendances.filter(timestamp__date=today).count()
            
            # This week's attendance for teacher's subjects
            week_start = today - timedelta(days=today.weekday())
            week_attendance = attendances.filter(timestamp__date__gte=week_start).count()
            
        else:
            # Student or other roles
            total_students = 0
            total_teachers = 0
            total_subjects = 0
            total_attendance = 0
            today_attendance = 0
            week_attendance = 0
        
        stats = {
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_subjects': total_subjects,
            'total_attendance': total_attendance,
            'today_attendance': today_attendance,
            'week_attendance': week_attendance,
            'user_role': user.role
        }
        
        return Response(stats)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_teacher_dashboard_stats(request):
    """Get detailed dashboard statistics for teacher"""
    user = request.user
    
    if user.role != 'teacher':
        return Response({
            'error': 'Only teachers can access this endpoint'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Get teacher's subjects
        teacher_subjects = TeacherSubject.objects.filter(
            teacher__teacher_code=user.teacher_code
        ).values_list('subject_id', flat=True)
        
        # Get students registered for teacher's subjects
        student_subjects = StudentSubject.objects.filter(
            subject_id__in=teacher_subjects
        )
        
        # Get attendance for teacher's subjects
        attendances = Attendance.objects.filter(subject_id__in=teacher_subjects)
        
        # Today's statistics
        today = datetime.now().date()
        today_attendances = attendances.filter(timestamp__date=today)
        
        # Calculate statistics
        total_students = student_subjects.values('student').distinct().count()
        total_subjects = len(teacher_subjects)
        total_attendance = attendances.count()
        today_attendance = today_attendances.count()
        
        # Today's attendance by status
        today_present = today_attendances.filter(status='present').count()
        today_absent = today_attendances.filter(status='absent').count()
        today_late = today_attendances.filter(status='late').count()
        
        # Calculate attendance rate
        attendance_rate = ((today_present / total_students) * 100) if total_students > 0 else 0
        
        stats = {
            'total_students': total_students,
            'total_subjects': total_subjects,
            'total_attendance': total_attendance,
            'today_attendance': today_attendance,
            'today_present': today_present,
            'today_absent': today_absent,
            'today_late': today_late,
            'attendance_rate': round(attendance_rate, 1),
            'teacher_code': user.teacher_code
        }
        
        return Response({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# DEBUG: Check teacher-subject relationships
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_student_subjects(request):
    """Get subjects registered by the current student"""
    user = request.user
    
    # Debug logging
    print(f"🔍 Debug get_current_student_subjects:")
    print(f"  User ID: {user.id}")
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Role: {getattr(user, 'role', 'NO_ROLE')}")
    print(f"  Student code: {getattr(user, 'student_code', 'NO_STUDENT_CODE')}")
    
    if not hasattr(user, 'role') or user.role != 'student':
        return Response({
            'error': f'Only students can access this endpoint. Current role: {getattr(user, "role", "NO_ROLE")}'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        print(f"🔍 Looking for student with code: {user.student_code}")
        
        # Get student by student_code
        student = Student.objects.get(student_code=user.student_code)
        print(f"✅ Found student: {student.name} (ID: {student.id})")
        
        # Get student's subject registrations
        student_subjects = StudentSubject.objects.filter(
            student=student
        ).select_related('subject')
        
        print(f"📚 Found {student_subjects.count()} subject registrations for student")
        
        data = []
        for ss in student_subjects:
            print(f"  - {ss.subject.subject_name} ({ss.subject.subject_code})")
            data.append({
                'id': ss.id,
                'subject_id': ss.subject.id,
                'subject_code': ss.subject.subject_code,
                'subject_name': ss.subject.subject_name,
                'credits': ss.subject.credits,
                'description': ss.subject.description,
                'semester': ss.semester,
                'academic_year': ss.academic_year,
                'created_at': ss.created_at
            })
        
        print(f"📤 Returning {len(data)} subjects")
        response_data = {
            'success': True,
            'data': data
        }
        print(f"📤 Response format: {type(response_data)}")
        print(f"📤 Response keys: {response_data.keys()}")
        print(f"📤 Data type: {type(response_data['data'])}")
        print(f"📤 Data length: {len(response_data['data'])}")
        return Response(response_data)
        
    except Student.DoesNotExist:
        return Response({
            'error': 'Student not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_teacher_students(request):
    """Get students registered for subjects taught by the current teacher"""
    user = request.user
    
    # Debug logging
    print(f"🔍 Debug get_teacher_students:")
    print(f"  User ID: {user.id}")
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Role: {getattr(user, 'role', 'NO_ROLE')}")
    print(f"  Teacher code: {getattr(user, 'teacher_code', 'NO_TEACHER_CODE')}")
    
    if not hasattr(user, 'role') or user.role != 'teacher':
        return Response({
            'error': f'Only teachers can access this endpoint. Current role: {getattr(user, "role", "NO_ROLE")}'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Get teacher's subjects
        teacher_subjects = TeacherSubject.objects.filter(
            teacher__teacher_code=user.teacher_code
        ).values_list('subject_id', flat=True)
        
        # Get students registered for these subjects
        student_subjects = StudentSubject.objects.filter(
            subject_id__in=teacher_subjects
        ).select_related('student', 'subject')
        
        # Get unique students with their details
        students_data = []
        seen_students = set()
        
        for ss in student_subjects:
            if ss.student.id not in seen_students:
                seen_students.add(ss.student.id)
                students_data.append({
                    'id': ss.student.id,
                    'student_code': ss.student.student_code,
                    'name': ss.student.name,
                    'student_class': ss.student.student_class,
                    'email': ss.student.email,
                    'phone_number': ss.student.phone_number,
                    'address': ss.student.address,
                    'dayofbirth': ss.student.dayofbirth,
                    'is_active': True,  # Default to active
                    'registered_subjects': []
                })
            
            # Add subject info to the student
            student_data = next(s for s in students_data if s['id'] == ss.student.id)
            student_data['registered_subjects'].append({
                'subject_id': ss.subject.id,
                'subject_name': ss.subject.subject_name,
                'subject_code': ss.subject.subject_code,
                'semester': ss.semester,
                'academic_year': ss.academic_year
            })
        
        return Response({
            'success': True,
            'data': students_data
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_teacher_subjects_bulk(request):
    """Create TeacherSubject records for all subjects for the first teacher"""
    try:
        # Get first teacher and all subjects
        teacher = Teacher.objects.first()
        if not teacher:
            return Response({
                'error': 'No teachers found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        subjects = Subject.objects.all()
        if not subjects.exists():
            return Response({
                'error': 'No subjects found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        created_count = 0
        existing_count = 0
        
        for subject in subjects:
            ts, created = TeacherSubject.objects.get_or_create(
                teacher=teacher,
                subject=subject,
                defaults={
                    'semester': '2024-1',
                    'academic_year': '2024-2025'
                }
            )
            if created:
                created_count += 1
            else:
                existing_count += 1
        
        return Response({
            'success': True,
            'message': f'Created {created_count} new TeacherSubject records, {existing_count} already existed',
            'teacher': {
                'name': teacher.name,
                'teacher_code': teacher.teacher_code
            },
            'total_subjects': subjects.count()
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def debug_user_info(request):
    """Debug endpoint to check current user information"""
    user = request.user
    
    user_info = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_active': user.is_active,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'date_joined': user.date_joined,
        'role': getattr(user, 'role', 'NO_ROLE'),
        'student_code': getattr(user, 'student_code', 'NO_STUDENT_CODE'),
        'teacher_code': getattr(user, 'teacher_code', 'NO_TEACHER_CODE'),
    }
    
    return Response({
        'success': True,
        'data': user_info
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def fix_user_role(request):
    """Fix user role based on teacher_code or student_code"""
    user = request.user
    
    try:
        # Check if user should be teacher
        if user.teacher_code:
            teacher = Teacher.objects.filter(teacher_code=user.teacher_code).first()
            if teacher and user.role != 'teacher':
                user.role = 'teacher'
                user.save()
                return Response({
                    'success': True,
                    'message': f'Fixed user role to teacher for {user.username}',
                    'old_role': user.role,
                    'new_role': 'teacher'
                })
        
        # Check if user should be student
        elif user.student_code:
            student = Student.objects.filter(student_code=user.student_code).first()
            if student and user.role != 'student':
                user.role = 'student'
                user.save()
                return Response({
                    'success': True,
                    'message': f'Fixed user role to student for {user.username}',
                    'old_role': user.role,
                    'new_role': 'student'
                })
        
        # Check if user should be admin
        elif user.is_superuser or user.is_staff:
            if user.role != 'admin':
                user.role = 'admin'
                user.save()
                return Response({
                    'success': True,
                    'message': f'Fixed user role to admin for {user.username}',
                    'old_role': user.role,
                    'new_role': 'admin'
                })
        
        return Response({
            'success': True,
            'message': 'User role is already correct',
            'current_role': user.role
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def debug_student_subjects(request):
    """Debug endpoint to check student subject data"""
    user = request.user
    
    debug_info = {
        'user_info': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': getattr(user, 'role', 'NO_ROLE'),
            'student_code': getattr(user, 'student_code', 'NO_STUDENT_CODE'),
        },
        'student_subjects_count': 0,
        'student_subjects': [],
        'all_student_subjects_count': 0,
        'all_students_count': 0,
        'all_users_with_student_code_count': 0
    }
    
    try:
        # Count all StudentSubject records
        debug_info['all_student_subjects_count'] = StudentSubject.objects.count()
        
        # Count all Students
        debug_info['all_students_count'] = Student.objects.count()
        
        # Count Users with student_code
        debug_info['all_users_with_student_code_count'] = User.objects.filter(
            student_code__isnull=False
        ).exclude(student_code='').count()
        
        # If user has student_code, check their subjects
        if hasattr(user, 'student_code') and user.student_code:
            try:
                student = Student.objects.get(student_code=user.student_code)
                student_subjects = StudentSubject.objects.filter(student=student).select_related('subject')
                debug_info['student_subjects_count'] = student_subjects.count()
                
                for ss in student_subjects:
                    debug_info['student_subjects'].append({
                        'id': ss.id,
                        'subject_name': ss.subject.subject_name,
                        'subject_code': ss.subject.subject_code,
                        'semester': ss.semester,
                        'academic_year': ss.academic_year,
                        'created_at': str(ss.created_at)
                    })
            except Student.DoesNotExist:
                debug_info['error'] = f'Student not found for code: {user.student_code}'
        
    except Exception as e:
        debug_info['error'] = str(e)
    
    return Response({
        'success': True,
        'data': debug_info
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def debug_teacher_subjects(request):
    """Debug endpoint to check teacher-subject relationships"""
    user = request.user
    
    if user.role != 'teacher':
        return Response({
            'error': 'Only teachers can access this debug endpoint'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Get teacher by teacher_code
    try:
        teacher = Teacher.objects.get(teacher_code=user.teacher_code)
    except Teacher.DoesNotExist:
        return Response({
            'error': 'Teacher not found',
            'teacher_code': user.teacher_code
        })
    
    # Get teacher subjects
    teacher_subjects = TeacherSubject.objects.filter(teacher=teacher)
    subject_ids = list(teacher_subjects.values_list('subject_id', flat=True))
    
    # Get subjects details
    subjects = Subject.objects.filter(id__in=subject_ids)
    
    # Get attendance for these subjects
    attendances = Attendance.objects.filter(subject_id__in=subject_ids)
    
    debug_data = {
        'user_info': {
            'username': user.username,
            'role': user.role,
            'teacher_code': user.teacher_code,
            'full_name': user.full_name
        },
        'teacher_info': {
            'id': teacher.id,
            'name': teacher.name,
            'teacher_code': teacher.teacher_code
        },
        'teacher_subjects': [
            {
                'id': ts.id,
                'subject_id': ts.subject.id,
                'subject_name': ts.subject.subject_name,
                'semester': ts.semester,
                'academic_year': ts.academic_year
            } for ts in teacher_subjects
        ],
        'subject_ids': subject_ids,
        'attendance_count': attendances.count(),
        'attendance_subjects': list(attendances.values_list('subject__subject_name', flat=True).distinct())
    }
    
    return Response(debug_data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_student_subject(request):
    """Register a student for a subject"""
    user = request.user
    
    if not hasattr(user, 'role') or user.role != 'student':
        return Response({
            'error': 'Only students can register for subjects'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        subject_id = request.data.get('subject_id')
        if not subject_id:
            return Response({
                'error': 'Subject ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get student
        student = Student.objects.get(student_code=user.student_code)
        
        # Get subject
        subject = Subject.objects.get(id=subject_id)
        
        # Check if already registered
        existing_registration = StudentSubject.objects.filter(
            student=student,
            subject=subject
        ).first()
        
        if existing_registration:
            return Response({
                'error': 'Student is already registered for this subject'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create registration
        student_subject = StudentSubject.objects.create(
            student=student,
            subject=subject,
            semester='2024-1',  # Default semester
            academic_year='2024-2025'  # Default academic year
        )
        
        return Response({
            'success': True,
            'message': f'Successfully registered for {subject.subject_name}',
            'registration_id': student_subject.id
        })
        
    except Student.DoesNotExist:
        return Response({
            'error': 'Student not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Subject.DoesNotExist:
        return Response({
            'error': 'Subject not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unregister_student_subject(request):
    """Unregister a student from a subject"""
    user = request.user
    
    if not hasattr(user, 'role') or user.role != 'student':
        return Response({
            'error': 'Only students can unregister from subjects'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        subject_id = request.data.get('subject_id')
        if not subject_id:
            return Response({
                'error': 'Subject ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get student
        student = Student.objects.get(student_code=user.student_code)
        
        # Get subject
        subject = Subject.objects.get(id=subject_id)
        
        # Find and delete registration
        registration = StudentSubject.objects.filter(
            student=student,
            subject=subject
        ).first()
        
        if not registration:
            return Response({
                'error': 'Student is not registered for this subject'
            }, status=status.HTTP_404_NOT_FOUND)
        
        registration.delete()
        
        return Response({
            'success': True,
            'message': f'Successfully unregistered from {subject.subject_name}'
        })
        
    except Student.DoesNotExist:
        return Response({
            'error': 'Student not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Subject.DoesNotExist:
        return Response({
            'error': 'Subject not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
