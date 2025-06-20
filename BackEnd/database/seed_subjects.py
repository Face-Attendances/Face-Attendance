import os
import django

# Khởi tạo môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BackEnd.settings')
django.setup()

from database.models import Subject

# Xoá dữ liệu cũ nếu cần
Subject.objects.all().delete()

# Dữ liệu mẫu
subjects = [
    ("An toàn thông tin", "Thứ 2 06:45-09:15"),
    ("Thiết kế cơ sở dữ liệu", "Thứ 3 09:25-11:55"),
    ("Cấu trúc rời rạc", "Thứ 4 06:45-09:15"),
    ("Kỹ thuật lập trình", "Thứ 5 13:00-15:00"),
    ("Cơ sở dữ liệu", "Thứ 6 12:10-14:40"),
    ("Mạng máy tính", "Thứ 2 09:25-11:55"),
    ("Trí tuệ nhân tạo", "Thứ 3 14:50-17:25"),
    ("Phân tích thiết kế hệ thống", "Thứ 4 17:30-20:00")
]

for name, time in subjects:
    Subject.objects.create(subject_name=name, time=time)

