# Hướng dẫn Import dữ liệu lên Railway

## Cách 1: Sử dụng Railway CLI

### 1. Cài đặt Railway CLI
```bash
npm install -g @railway/cli
```

### 2. Đăng nhập Railway
```bash
railway login
```

### 3. Link project
```bash
railway link
```

### 4. Chạy script import
```bash
railway run python railway_import.py
```

## Cách 2: Sử dụng Railway Dashboard

### 1. Truy cập Railway Dashboard
- Vào https://railway.app/dashboard
- Chọn project của bạn

### 2. Mở terminal
- Click vào service Django
- Chọn tab "Deployments"
- Click "Deploy" để deploy code mới

### 3. Chạy script
- Trong terminal, chạy:
```bash
python railway_import.py
```

## Cách 3: Sử dụng Django Management Command

### 1. Tạo management command
Tạo file `BackEnd/database/management/commands/import_railway_data.py`:

```python
from django.core.management.base import BaseCommand
from railway_import import import_sample_data

class Command(BaseCommand):
    help = 'Import sample data to Railway database'

    def handle(self, *args, **options):
        import_sample_data()
        self.stdout.write(
            self.style.SUCCESS('Successfully imported sample data')
        )
```

### 2. Chạy command
```bash
python manage.py import_railway_data
```

## Dữ liệu sẽ được import:

### Users:
- **Admin**: username: `admin`, password: `admin123`
- **Students**: 
  - `098765432111` / `18112005` (Ngô Thanh Tân)
  - `098765432112` / `18112005` (Ngô Thanh Tân2)
  - `098765432113` / `18112005` (Ngô Thanh Tân5)
  - `098765432115` / `18112005` (Ngô Thanh Tân999)
- **Teachers**:
  - `GV001` / `teacher123` (Giảng viên 1)
  - `GV002` / `teacher123` (Giảng viên 2)

### Subjects:
- CS101: Lập trình cơ bản
- CS102: Cơ sở dữ liệu
- CS103: Lập trình Web
- CS104: Mạng máy tính
- CS105: Hệ điều hành
- CS106: Cấu trúc dữ liệu
- CS107: Thuật toán
- CS108: Lập trình hướng đối tượng

### Relationships:
- Student-Subject assignments
- Teacher-Subject assignments
- Sample attendance records

## Lưu ý:
- Script sẽ tạo dữ liệu mới nếu chưa tồn tại
- Nếu dữ liệu đã tồn tại, script sẽ bỏ qua
- Đảm bảo đã migrate database trước khi chạy script 