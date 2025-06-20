from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()

# 1. Nếu đã có User được register, unregister nó
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

# 2. Đăng ký lại với 1 class duy nhất
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = (
        'username','email','full_name','student_code',
        'address','phone_number','student_class',
        'is_staff','is_active'
    )
    list_filter = ('is_staff', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Thông tin bổ sung', {
            'fields': (
                'full_name','student_code',
                'address','phone_number','student_class',
            ),
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Thông tin bổ sung', {
            'fields': (
                'full_name','student_code',
                'address','phone_number','student_class',
            ),
        }),
    )
