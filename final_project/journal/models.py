from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    class Roles(models.TextChoices):
        STUDENT='student','Студент'
        TEACHER='teacher','Мұғалім'
        ADMIN='admin','Администратор'
    role=models.CharField(max_length=20,choices=Roles.choices,default=Roles.STUDENT)
    full_name=models.CharField(max_length=255,blank=True)
    failed_login_attempts=models.PositiveIntegerField(default=0)
    locked_until=models.DateTimeField(null=True,blank=True)
    def is_locked(self):
        return bool(self.locked_until and self.locked_until > timezone.now())
    def __str__(self):
        return self.full_name or self.username

class Group(models.Model):
    name=models.CharField(max_length=100,unique=True)
    def __str__(self): return self.name

class Subject(models.Model):
    name=models.CharField(max_length=150)
    code=models.CharField(max_length=30,blank=True)
    teacher=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='subjects')
    groups=models.ManyToManyField(Group,related_name='subjects',blank=True)
    def __str__(self): return self.name

class StudentProfile(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='student_profile')
    group=models.ForeignKey(Group,on_delete=models.SET_NULL,null=True,blank=True,related_name='students')
    def __str__(self): return f'{self.user} - {self.group}'

class Grade(models.Model):
    student=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='grades')
    subject=models.ForeignKey(Subject,on_delete=models.CASCADE,related_name='grades')
    rk1=models.PositiveIntegerField(default=0,validators=[MinValueValidator(0),MaxValueValidator(100)])
    rk2=models.PositiveIntegerField(default=0,validators=[MinValueValidator(0),MaxValueValidator(100)])
    exam=models.PositiveIntegerField(default=0,validators=[MinValueValidator(0),MaxValueValidator(100)])
    attendance=models.PositiveIntegerField(default=100,validators=[MinValueValidator(0),MaxValueValidator(100)])
    updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        unique_together=('student','subject')
        ordering=['student__full_name','student__username']
    @property
    def final(self):
        return round(self.rk1*0.3 + self.rk2*0.3 + self.exam*0.4)
    def __str__(self): return f'{self.student} - {self.subject}'

class AuditLog(models.Model):
    class Actions(models.TextChoices):
        CREATE='CREATE','CREATE'
        UPDATE='UPDATE','UPDATE'
        DELETE='DELETE','DELETE'
        LOGIN='LOGIN','LOGIN'
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True)
    action=models.CharField(max_length=20,choices=Actions.choices)
    entity=models.CharField(max_length=255)
    old_value=models.TextField(blank=True)
    new_value=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-created_at']

class PasswordResetCode(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    code=models.CharField(max_length=6)
    created_at=models.DateTimeField(auto_now_add=True)
    is_used=models.BooleanField(default=False)
    def is_valid(self):
        return (not self.is_used) and (timezone.now()-self.created_at).total_seconds() <= 600
