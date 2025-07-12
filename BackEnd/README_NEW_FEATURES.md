# Hướng dẫn sử dụng các chức năng mới

## 1. User Admin mặc định

Đã tạo user admin mặc định với thông tin:
- **Username**: admin
- **Password**: Admin@1234
- **Role**: admin

### Tạo user admin mới:
```bash
python manage.py create_admin
```

## 2. Auto Training Service

### API Endpoints:

#### 1. Auto Training với nhiều ảnh
**POST** `/api/detection/auto-training/`

**Form Data:**
- `student_id`: ID của student
- `subject_id`: ID của subject  
- `images`: List các file ảnh (multiple files)

**Response:**
```json
{
    "success": true,
    "message": "Training thành công cho [Tên Student]",
    "folder_path": "/path/to/training/folder",
    "images_count": 5
}
```

#### 2. Kiểm tra trạng thái training
**GET** `/api/detection/training-status/{student_id}/`

**Response:**
```json
{
    "success": true,
    "data": {
        "status": "completed",
        "folder_path": "/path/to/folder",
        "images_count": 5,
        "created_at": "2024-01-01T10:00:00Z"
    }
}
```

### Tính năng:
- Tự động tạo folder theo format: `student_code_fullname`
- Lưu ảnh training với timestamp
- Tạo face encodings từ ảnh
- Lưu trữ trạng thái training session

## 3. Attendance với Confidence Score

### API Endpoint:

**POST** `/api/detection/attendance-confidence/`

**Form Data:**
- `image`: File ảnh
- `subject_name`: Tên môn học
- `detected_by`: ID của user thực hiện (optional)

**Response:**
```json
{
    "success": true,
    "results": [
        {
            "student_code": "SV001",
            "student_name": "Nguyễn Văn A",
            "confidence": 95.5,
            "status": "present"
        }
    ],
    "image_path": "/path/to/attendance/image.jpg"
}
```

### Tính năng:
- Hiển thị tỉ lệ % phát hiện khuôn mặt
- Tự động lưu ảnh điểm danh
- Lưu thông tin người thực hiện
- So sánh với encodings đã training

## 4. Lịch sử điểm danh theo Role

### API Endpoints:

#### 1. Lịch sử điểm danh theo role
**GET** `/api/database/attendance/history/`

**Query Parameters:**
- `days`: Số ngày gần nhất (mặc định: 30)

**Response theo Role:**

**Admin:**
```json
{
    "success": true,
    "data": [...], // Tất cả attendance records
    "stats": {
        "total_records": 100,
        "present_count": 85,
        "absent_count": 10,
        "late_count": 5,
        "present_rate": 85.0,
        "avg_face_detection_confidence": 92.5
    },
    "role": "admin"
}
```

**Teacher:**
```json
{
    "success": true,
    "data": [...], // Attendance của các môn học mình dạy
    "stats": {...},
    "role": "teacher"
}
```

**Student:**
```json
{
    "success": true,
    "data": [...], // Chỉ attendance của mình
    "stats": {...},
    "role": "student"
}
```

#### 2. Lịch sử điểm danh theo môn học
**GET** `/api/database/attendance/subject/{subject_name}/`

#### 3. Tổng quan điểm danh
**GET** `/api/database/attendance/summary/`

**Query Parameters:**
- `days`: Số ngày gần nhất (mặc định: 30)

#### 4. Training Sessions
**GET** `/api/database/training-sessions/`

## 5. Cấu trúc thư mục

```
BackEnd/
├── media/
│   ├── training_data/
│   │   └── student_code_fullname/
│   │       ├── training_1_20240101_100000.jpg
│   │       └── training_2_20240101_100100.jpg
│   ├── encodings/
│   │   └── student_code_encodings.npy
│   └── attendance_images/
│       └── attendance_20240101_100000.jpg
```

## 6. Database Models mới

### Attendance (cập nhật):
- `face_detection_confidence`: Tỉ lệ phát hiện khuôn mặt (%)
- `detected_by`: User thực hiện điểm danh
- `image_path`: Đường dẫn ảnh điểm danh
- `notes`: Ghi chú

### Subject (cập nhật):
- `teacher`: Giảng viên phụ trách môn học

### TrainingSession (mới):
- `student`: Student được training
- `subject`: Môn học
- `folder_path`: Đường dẫn folder training
- `status`: Trạng thái (pending/processing/completed/failed)
- `images_count`: Số lượng ảnh training

## 7. Quyền truy cập theo Role

### Admin:
- Xem tất cả lịch sử điểm danh
- Xem tất cả training sessions
- Xem tổng quan toàn bộ hệ thống

### Teacher:
- Xem lịch sử điểm danh của các môn học mình dạy
- Xem training sessions của các môn học mình dạy
- Xem tổng quan các môn học mình phụ trách

### Student:
- Xem lịch sử điểm danh của mình
- Xem training sessions của mình
- Xem tổng quan điểm danh cá nhân

## 8. Sử dụng Frontend

Để sử dụng các API này từ frontend, bạn cần:

1. **Auto Training:**
   - Upload nhiều ảnh cùng lúc
   - Chọn student và subject
   - Hiển thị progress và kết quả

2. **Attendance với Confidence:**
   - Chụp ảnh hoặc upload ảnh
   - Hiển thị kết quả với confidence score
   - Lưu lịch sử

3. **Lịch sử điểm danh:**
   - Hiển thị theo role của user
   - Filter theo thời gian
   - Hiển thị thống kê

## 9. Lưu ý

- Đảm bảo đã cài đặt `face_recognition` library
- Cần có đủ quyền ghi vào thư mục media
- Threshold cho face detection: 0.6 (có thể điều chỉnh)
- Format folder: `student_code_fullname` (thay space bằng underscore) 