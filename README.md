| Lệnh                                            | Chức năng                                                                         |
| ----------------------------------------------- | --------------------------------------------------------------------------------- |
| django-admin startproject <name> .          | Khởi tạo một Django project mới (dùng dấu . để tạo ngay trong thư mục hiện tại) |
| python manage.py startapp <app>             | Tạo một Django app con mới                                                        |
| python manage.py runserver                  | Chạy development server tại http://127.0.0.1:8000/                            |
| python manage.py makemigrations             | Sinh các file migration từ thay đổi models.py                                 |
| python manage.py migrate                    | Áp dụng các migration vào database                                                |
| python manage.py showmigrations             | Hiển thị danh sách migration và trạng thái đã/applied                             |
| python manage.py sqlmigrate <app> <migration> | Xem SQL tương ứng với một migration cụ thể                                        |
| python manage.py createsuperuser            | Tạo tài khoản admin (superuser) cho site                                          |
| python manage.py shell                      | Mở Python shell với Django context (có thể import model, settings…)               |
| python manage.py dbshell                    | Mở shell của database (MySQL/SQLite/PostgreSQL…)                                  |
| python manage.py collectstatic              | Thu gom toàn bộ file static (CSS/JS/images) ra thư mục STATIC_ROOT            |
| python manage.py test                       | Chạy unit tests cho project/app                                                   |
| python manage.py check                      | Kiểm tra cấu hình, URL, models… xem có cảnh báo/lỗi không                         |
| python manage.py flush                      | Xóa toàn bộ dữ liệu trong database (chú ý: irreversible!)                         |
| python manage.py dumpdata [app.Model]       | Xuất dữ liệu ra JSON (toàn bộ hoặc cụ thể model)                                  |
| python manage.py loaddata <fixture.json>    | Nạp dữ liệu từ file fixture (JSON/YAML/XML)                                       |
| python manage.py makemessages -l <lang>     | Sinh file dịch (i18n) cho ngôn ngữ <lang> (ví dụ vi)                          |
| python manage.py compilemessages            | Biên dịch lại file .po thành .mo cho i18n                                     |


chạy cam = python manage.py run_attendance   
chạy train = python manage.py train_encodings
dùng khi chỉnh DB = python manage.py migrate 
chạy server (test Postman) = python manage.py runserver
Tạo tài khoản admin (superuser) cho site = python manage.py createsuperuser      
       
Superuser updated: username=admin, student_code=123456789012