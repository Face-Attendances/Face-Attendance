from django.db import models
from django.db import migrations
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    full_name = models.CharField(max_length=100, blank=True)
    student_code = models.CharField(max_length=20, blank=True, null=True, unique=True)
    student = models.ForeignKey(
        'database.Student',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='StudentUser'
    )
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    student_class = models.CharField(max_length=50, blank=True)
    email = models.EmailField(max_length=254, unique=True)

    REQUIRED_FIELDS = ['email', 'student_code']
    
    ROLE_CHOICES = [
        ('student', 'Sinh viên'),
        ('teacher', 'Giảng viên'),
        ('admin', 'Quản trị'),
    ]
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',
    )

    def __str__(self):
        return self.username


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('username', models.CharField(max_length=150, unique=True)),
                ('first_name', models.CharField(max_length=150, blank=True)),
                ('last_name', models.CharField(max_length=150, blank=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('full_name', models.CharField(max_length=100, blank=True)),
                ('student_code', models.CharField(max_length=20, blank=True, unique=True)),
                ('student', models.ForeignKey('database.Student', on_delete=models.CASCADE, null=True, blank=True, related_name='StudentUser')),
            ],
            options={'abstract': False},
        ),
    ]
