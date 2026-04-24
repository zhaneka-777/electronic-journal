from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify-code/', views.verify_code_view, name='verify_code'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('grades/', views.grades_view, name='grades'),
    path('teacher-journal/', views.teacher_journal_view, name='teacher_journal'),
    path('teacher-journal/<int:grade_id>/edit/', views.edit_grade_view, name='edit_grade'),
    path('audit-log/', views.audit_log_view, name='audit_log'),
    path('profile/', views.profile_view, name='profile'),
    path('export/excel/', views.export_excel_view, name='export_excel'),
    path('export/pdf/', views.export_pdf_view, name='export_pdf'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]
