from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentSubjectList, StudentViewSet, TeacherSubjectList, mark_attendance, today_attendance, attendance_logs, SubjectListAPIView

router = DefaultRouter()
router.register('students', StudentViewSet, basename='student')

urlpatterns = [
    path('', include(router.urls)),
    path('attendance/mark/',    mark_attendance,    name='api-mark-attendance'),
    path('attendance/today/',   today_attendance,   name='api-today-attendance'),
    path('attendance/logs/',    attendance_logs,    name='api-attendance-logs'),
    path('subjects/', SubjectListAPIView.as_view(), name='subject-list'),
    path('subjects/student/', StudentSubjectList.as_view(), name='student-subject-list'),
    path('subjects/teacher/', TeacherSubjectList.as_view(), name='teacher-subject-list'),
]