from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import AuditLog, Grade, Group, PasswordResetCode, StudentProfile, Subject, User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (("Қосымша", {'fields': ('role','full_name','failed_login_attempts','locked_until')}),)
    list_display=('username','full_name','role','is_staff','is_active')

admin.site.register(Group)
admin.site.register(Subject)
admin.site.register(StudentProfile)
admin.site.register(Grade)
admin.site.register(AuditLog)
admin.site.register(PasswordResetCode)
