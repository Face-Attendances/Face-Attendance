from django.db import models

class Student(models.Model):
    student_code    = models.CharField(max_length=20, unique=True)
    name          = models.CharField(max_length=100)
    student_class = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.student_code} – {self.name}"

class Attendance(models.Model):
    student   = models.ForeignKey(
        'database.Student',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    subject   = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    status    = models.CharField(max_length=10, choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ])

    class Meta:
        db_table = 'database_attendance'
        
class Subject(models.Model):
    subject_name = models.CharField(max_length=100)
    time = models.CharField(max_length=100)
    for_teacher = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject_name} ({'GV' if self.for_teacher else 'SV'})"
