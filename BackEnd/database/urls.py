from django.urls import path
from . import views

urlpatterns = [
    # Student management
    path('students/', views.get_students, name='get_students'),
    path('students/create/', views.create_student, name='create_student'),
    path('students/<str:student_code>/update/', views.update_student_by_code, name='update_student_by_code'),
    path('students/<str:student_code>/delete/', views.delete_student_by_code, name='delete_student_by_code'),
    
    # Teacher management
    path('teachers/', views.get_teachers, name='get_teachers'),
    path('teachers/create/', views.create_teacher, name='create_teacher'),
    path('teachers/<str:teacher_code>/update/', views.update_teacher_by_code, name='update_teacher_by_code'),
    path('teachers/<str:teacher_code>/delete/', views.delete_teacher_by_code, name='delete_teacher_by_code'),
    
    # Subject management
    path('subjects/', views.get_subjects, name='get_subjects'),
    path('subjects/create/', views.create_subject, name='create_subject'),
    path('subjects/<int:subject_id>/update/', views.update_subject, name='update_subject'),
    path('subjects/<int:subject_id>/delete/', views.delete_subject, name='delete_subject'),
    path('subjects/<int:subject_id>/students/', views.get_subject_students, name='get_subject_students'),
    
    # Teacher Subject relationships
    path('teacher-subjects/', views.get_teacher_subjects, name='get_teacher_subjects'),
    path('teacher-subjects/create/', views.create_teacher_subject, name='create_teacher_subject'),
    path('teacher-subjects/<int:teacher_subject_id>/', views.get_teacher_subject_detail, name='get_teacher_subject_detail'),
    path('teacher-subjects/<int:teacher_subject_id>/update/', views.update_teacher_subject, name='update_teacher_subject'),
    path('teacher-subjects/<int:teacher_subject_id>/delete/', views.delete_teacher_subject, name='delete_teacher_subject'),
    path('teacher-subjects/teaching/', views.get_teacher_teaching_subjects, name='get_teacher_teaching_subjects'),
    path('teacher-subjects/details/', views.get_teacher_subjects_with_details, name='get_teacher_subjects_with_details'),
    
    # Student Subject relationships
    path('student-subjects/', views.get_student_subjects_with_details, name='get_student_subjects_with_details'),
    path('student-subjects/create/', views.create_student_subject, name='create_student_subject'),
    path('student-subjects/<int:student_subject_id>/', views.get_student_subject_detail, name='get_student_subject_detail'),
    path('student-subjects/<int:student_subject_id>/update/', views.update_student_subject, name='update_student_subject'),
    path('student-subjects/<int:student_subject_id>/delete/', views.delete_student_subject, name='delete_student_subject'),
    
    # Attendance
    path('attendance/', views.get_attendance_logs, name='get_attendance_logs'),
    path('attendance/create/', views.create_attendance, name='create_attendance'),
    path('attendance/<int:log_id>/delete/', views.get_attendance_log_detail, name='delete_attendance'),
    path('attendance/summary/', views.get_attendance_summary, name='get_attendance_summary'),
    path('attendance/statistics/', views.get_attendance_summary, name='get_attendance_statistics'),
    path('attendance/history/', views.get_attendance_history, name='get_attendance_history'),
    path('attendance/teacher/', views.get_teacher_attendance, name='get_teacher_attendance'),
    
    # Training
    path('training-sessions/', views.get_training_sessions, name='get_training_sessions'),
    path('training-sessions/create/', views.create_training_session, name='create_training_session'),
    
    # Dashboard
    path('dashboard/stats/', views.get_dashboard_stats, name='get_dashboard_stats'),
    path('dashboard/teacher-stats/', views.get_teacher_dashboard_stats, name='get_teacher_dashboard_stats'),
    
    # Teacher specific endpoints
    path('teacher/students/', views.get_teacher_students, name='get_teacher_students'),
    
    # Student specific endpoints
    path('student/my-subjects/', views.get_current_student_subjects, name='get_current_student_subjects'),
    path('student/register-subject/', views.register_student_subject, name='register_student_subject'),
    path('student/unregister-subject/', views.unregister_student_subject, name='unregister_student_subject'),
    
    # Debug
    path('debug/user-info/', views.debug_user_info, name='debug_user_info'),
    path('debug/student-subjects/', views.debug_student_subjects, name='debug_student_subjects'),
    path('fix-user-role/', views.fix_user_role, name='fix_user_role'),
    path('debug/teacher-subjects/', views.debug_teacher_subjects, name='debug_teacher_subjects'),
    path('create-teacher-subjects-bulk/', views.create_teacher_subjects_bulk, name='create_teacher_subjects_bulk'),
]

# Add attendance log URLs
urlpatterns += [
    path('attendance/log/', views.get_attendance_logs, name='get_attendance_log'),
    path('attendance/log/<int:log_id>/', views.get_attendance_log_detail, name='get_attendance_log_detail'),
]