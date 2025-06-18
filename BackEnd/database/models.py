from django.db import models

class Student(models.Model):
    student_id    = models.CharField(max_length=20, unique=True)
    name          = models.CharField(max_length=100)
    student_class = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.student_id} – {self.name}"

class Attendance(models.Model):
    student   = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject   = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    