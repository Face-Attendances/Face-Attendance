# FrontEnd - Face Attendance System

## 📁 Cấu trúc thư mục

```
FrontEnd/
├── assets/                 # Tài nguyên tĩnh
│   ├── images/            # Hình ảnh, logo
│   ├── icons/             # Icons (nếu có)
│   └── fonts/             # Fonts (nếu có)
├── shared/                # Tài nguyên dùng chung
│   ├── css/               # CSS dùng chung
│   │   ├── shared.css     # Components chung
│   │   ├── layout.css     # Layout chung
│   │   └── variables.css  # CSS variables
│   ├── js/                # JavaScript dùng chung
│   │   ├── jquery-3.7.1.min.js
│   │   ├── utils.js       # Utility functions
│   │   └── api.js         # API helpers
│   └── components/        # HTML components
├── login/                 # Trang đăng nhập
│   ├── login.html
│   ├── login.css
│   ├── login.js
│   ├── forgot-password.html
│   └── forgot.js
├── student/               # Trang sinh viên
│   ├── dashboard.html
│   ├── profile.html
│   ├── change_password.html
│   ├── course-registration.html
│   ├── student.css
│   └── student.js
├── teacher/               # Trang giảng viên
│   ├── dashboard.html
│   ├── profile.html
│   ├── change_password.html
│   ├── teacher.css
│   └── teacher.js
├── admin/                 # Trang admin
│   ├── overview.html
│   ├── students.html
│   ├── teachers.html
│   ├── subjects.html
│   ├── admin.css
│   └── admin.js
├── docs/                  # Tài liệu
│   ├── README.md
│   ├── API.md
│   └── DEPLOYMENT.md
└── tests/                 # File test
    ├── test_login.html
    ├── test_change_password.html
    └── test_api.html
```

## 🎨 Bảng màu

### Primary Colors:
- **Peru**: `#C26B32` - Màu cam nâu ấm áp
- **Light Steel Blue**: `#A6BCD8` - Màu xanh nhạt dịu mắt  
- **Gainsboro**: `#E8E8E7` - Màu xám nhạt gần trắng
- **Cadet Blue**: `#6495A6` - Màu xanh xám trung tính
- **Dark Slate Gray**: `#2F343D` - Màu xám đen tối

### Usage:
- **Background gradients**: `#E8E8E7` → `#A6BCD8`
- **Primary buttons**: `#C26B32` → `#6495A6`
- **Form borders**: `#A6BCD8`
- **Focus states**: `#C26B32`
- **Text primary**: `#2F343D`
- **Text secondary**: `#6495A6`

## 🚀 Cách sử dụng

### 1. Chạy script tổ chức lại:
```bash
cd FrontEnd
reorganize.bat
```

### 2. Cập nhật đường dẫn trong HTML:
```html
<!-- CSS -->
<link rel="stylesheet" href="../shared/css/shared.css">
<link rel="stylesheet" href="../shared/css/layout.css">

<!-- JavaScript -->
<script src="../shared/js/jquery-3.7.1.min.js"></script>
<script src="../shared/js/utils.js"></script>

<!-- Images -->
<img src="../assets/images/logo.png" alt="Logo">
```

### 3. Import shared components:
```html
<!-- Trong HTML files -->
<link rel="stylesheet" href="../shared/css/shared.css">
<link rel="stylesheet" href="../shared/css/layout.css">
```

## 📋 Quy tắc đặt tên

### Files:
- **HTML**: `kebab-case.html` (ví dụ: `course-registration.html`)
- **CSS**: `kebab-case.css` (ví dụ: `student-dashboard.css`)
- **JS**: `kebab-case.js` (ví dụ: `api-helpers.js`)

### Classes:
- **Components**: `.component-name` (ví dụ: `.login-form`)
- **States**: `.component-name--state` (ví dụ: `.btn--disabled`)
- **Modifiers**: `.component-name__element` (ví dụ: `.card__header`)

## 🔧 Development

### 1. Thêm component mới:
```bash
# Tạo file CSS
touch shared/css/new-component.css

# Tạo file JS
touch shared/js/new-component.js

# Import trong HTML
<link rel="stylesheet" href="../shared/css/new-component.css">
<script src="../shared/js/new-component.js"></script>
```

### 2. Thêm trang mới:
```bash
# Tạo folder cho role mới
mkdir new-role/

# Tạo files
touch new-role/dashboard.html
touch new-role/new-role.css
touch new-role/new-role.js
```

### 3. Testing:
```bash
# Chạy test
cd tests/
python -m http.server 8000
# Mở browser: http://localhost:8000/test_change_password.html
```

## 📝 Notes

- Tất cả shared resources phải ở trong `shared/`
- Mỗi role có folder riêng với CSS/JS riêng
- Sử dụng relative paths (`../`) để link resources
- Test files ở trong `tests/`
- Documentation ở trong `docs/`

## 🐛 Troubleshooting

### Path issues:
- Kiểm tra relative paths trong HTML
- Đảm bảo file tồn tại ở đúng vị trí
- Sử dụng browser dev tools để debug

### CSS conflicts:
- Sử dụng CSS specificity
- Kiểm tra thứ tự import CSS
- Sử dụng CSS variables cho consistency

### JavaScript errors:
- Kiểm tra console errors
- Đảm bảo jQuery loaded trước custom JS
- Sử dụng try-catch cho API calls 