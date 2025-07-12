from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import User

User = get_user_model()

class Command(BaseCommand):
    help = 'Tạo user admin mặc định'

    def handle(self, *args, **options):
        try:
            # Kiểm tra xem admin đã tồn tại chưa
            if User.objects.filter(username='admin1').exists():
                self.stdout.write(
                    self.style.WARNING('User admin1 đã tồn tại!')
                )
                return

            # Tạo user admin
            admin_user = User.objects.create_user(
                username='admin1',
                email='admin@example.com',
                password='Admin@1234',
                full_name='Administrator',
                role='admin',
                is_staff=True,
                is_superuser=True
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Đã tạo user admin thành công!\n'
                    f'Username: admin1\n'
                    f'Password: Admin@1234\n'
                    f'Role: admin'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Lỗi khi tạo user admin: {str(e)}')
            ) 