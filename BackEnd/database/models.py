
from django.db import models
from django.conf import settings

class Attendance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    present = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} @ {self.timestamp}"
