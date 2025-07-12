from django.urls import path
from . import views

urlpatterns = [
    # Student management
    path('students/', views.get_students, name='get_students'),
    path('students/create/', views.create_student, name='create_student'),
    path('students/<int:student_id>/update/', views.update_student, name='update_student'),
    path('students/<int:student_id>/delete/', views.delete_student, name='delete_student'),
    
    # Teacher management
    path('teachers/', views.get_teachers, name='get_teachers'),
    path('teachers/create/', views.create_teacher, name='create_teacher'),
    path('teachers/<int:teacher_id>/update/', views.update_teacher, name='update_teacher'),
    path('teachers/<int:teacher_id>/delete/', views.delete_teacher, name='delete_teacher'),
    
    # Subject management
    path('subjects/', views.get_subjects, name='get_subjects'),
    path('subjects/create/', views.create_subject, name='create_subject'),
    path('subjects/<int:subject_id>/update/', views.update_subject, name='update_subject'),
    path('subjects/<int:subject_id>/delete/', views.delete_subject, name='delete_subject'),
    
    # Teacher Subject relationships
    path('teacher-subjects/', views.get_teacher_subjects, name='get_teacher_subjects'),
    path('teacher-subjects/create/', views.create_teacher_subject, name='create_teacher_subject'),
    
    # Student Subject relationships
    path('student-subjects/', views.get_student_subjects, name='get_student_subjects'),
    path('student-subjects/create/', views.create_student_subject, name='create_student_subject'),
    
    # Attendance
    path('attendance/', views.get_attendance_logs, name='get_attendance_logs'),
    path('attendance/create/', views.create_attendance, name='create_attendance'),
    path('attendance/summary/', views.get_attendance_summary, name='get_attendance_summary'),
    path('attendance/history/', views.get_attendance_history, name='get_attendance_history'),
    
    # Training
    path('training-sessions/', views.get_training_sessions, name='get_training_sessions'),
    path('training-sessions/create/', views.create_training_session, name='create_training_session'),
    
    # Dashboard
    path('dashboard/stats/', views.get_dashboard_stats, name='get_dashboard_stats'),
]

# Add attendance log URLs
urlpatterns += [
    path('attendance/log/', views.get_attendance_logs, name='get_attendance_log'),
    path('attendance/log/<int:log_id>/', views.get_attendance_log_detail, name='get_attendance_log_detail'),
]