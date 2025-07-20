from django.core.management.base import BaseCommand
from database.models import Teacher
from users.models import User

class Command(BaseCommand):
    help = 'Create user account for teacher'

    def handle(self, *args, **options):
        self.stdout.write('Creating teacher user account...')
        
        try:
            # Get the teacher from sample data
            teacher = Teacher.objects.filter(teacher_code='123456789012').first()
            if not teacher:
                self.stdout.write(
                    self.style.ERROR('Teacher not found. Please run create_sample_data first.')
                )
                return
            
            # Create user account for teacher
            user, created = User.objects.get_or_create(
                teacher_code=teacher.teacher_code,
                defaults={
                    'username': teacher.teacher_code,
                    'full_name': teacher.name,
                    'email': teacher.email,
                    'role': 'teacher',
                    'is_staff': True
                }
            )
            
            if created:
                # Set password (using dayofbirth format if available)
                if teacher.dayofbirth:
                    try:
                        day, month, year = teacher.dayofbirth.split('/')
                        password = f"{day}{month}{year}"
                    except:
                        password = "123456"  # Default password
                else:
                    password = "123456"  # Default password
                
                user.set_password(password)
                user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'Created user account for teacher: {teacher.name}')
                )
                self.stdout.write(f'Username: {user.username}')
                self.stdout.write(f'Password: {password}')
            else:
                self.stdout.write(
                    self.style.WARNING(f'User account already exists for teacher: {teacher.name}')
                )
                self.stdout.write(f'Username: {user.username}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating teacher user account: {str(e)}')
            ) 