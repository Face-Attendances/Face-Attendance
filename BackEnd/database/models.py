from django.db import models
from users.models import User

class Student(models.Model):
    """Table database_student - lưu thông tin sinh viên"""
    student_code = models.CharField(max_length=12, unique=True, help_text="12-digit student code")
    name = models.CharField(max_length=100)
    student_class = models.CharField(max_length=50)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    dayofbirth = models.CharField(max_length=10, blank=True, help_text="Format: dd/mm/yyyy")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'database_student'
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    def __str__(self):
        return f"{self.student_code} – {self.name}"

class Teacher(models.Model):
    """Table database_teacher - lưu thông tin giảng viên"""
    teacher_code = models.CharField(max_length=12, unique=True, help_text="12-digit teacher code")
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    dayofbirth = models.CharField(max_length=10, blank=True, help_text="Format: dd/mm/yyyy")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'database_teacher'
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'

    def __str__(self):
        return f"{self.teacher_code} – {self.name}"

class Subject(models.Model):
    """Table database_subject - lưu thông tin môn học"""
    subject_code = models.CharField(max_length=20, unique=True)
    subject_name = models.CharField(max_length=100)
    credits = models.IntegerField(default=3)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'database_subject'
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'

    def __str__(self):
        return f"{self.subject_code} – {self.subject_name}"

class TeacherSubject(models.Model):
    """Table teacher_subject - lưu môn học mà giảng viên đăng ký"""
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='teacher_subjects')
    semester = models.CharField(max_length=20, blank=True)
    academic_year = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'teacher_subject'
        unique_together = ['teacher', 'subject', 'semester', 'academic_year']
        verbose_name = 'Teacher Subject'
        verbose_name_plural = 'Teacher Subjects'

    def __str__(self):
        return f"{self.teacher.name} - {self.subject.subject_name}"

class StudentSubject(models.Model):
    """Table student_subject - lưu môn học mà sinh viên đăng ký"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='student_subjects')
    semester = models.CharField(max_length=20, blank=True)
    academic_year = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'student_subject'
        unique_together = ['student', 'subject', 'semester', 'academic_year']
        verbose_name = 'Student Subject'
        verbose_name_plural = 'Student Subjects'

    def __str__(self):
        return f"{self.student.name} - {self.subject.subject_name}"

class Attendance(models.Model):
    """Table database_attendance - lưu lịch sử điểm danh"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='attendances')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='conducted_attendances')
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ])
    face_detection_confidence = models.FloatField(default=0.0, help_text="Tỉ lệ phát hiện khuôn mặt (%)")
    detected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_records'
    )
    image_path = models.CharField(max_length=500, blank=True, help_text="Đường dẫn ảnh điểm danh")
    notes = models.TextField(blank=True, help_text="Ghi chú")

    class Meta:
        db_table = 'database_attendance'
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'

    def __str__(self):
        return f"{self.student.name} - {self.subject.subject_name} - {self.timestamp}"

class TrainingSession(models.Model):
    """Model để lưu thông tin về các phiên training"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='training_sessions')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='training_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    folder_path = models.CharField(max_length=500, help_text="Đường dẫn folder training")
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Chờ xử lý'),
        ('processing', 'Đang xử lý'),
        ('completed', 'Hoàn thành'),
        ('failed', 'Thất bại'),
    ], default='pending')
    images_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'database_training_session'
        verbose_name = 'Training Session'
        verbose_name_plural = 'Training Sessions'

    def __str__(self):
        return f"{self.student.name} - {self.subject.subject_name} - {self.status}"
