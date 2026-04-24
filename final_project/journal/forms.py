from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Grade, User

class LoginForm(AuthenticationForm):
    role=forms.ChoiceField(choices=User.Roles.choices,label='Рөл')
    username=forms.CharField(label='Email / Логин')
    password=forms.CharField(widget=forms.PasswordInput,label='Құпиясөз')
    def confirm_login_allowed(self,user):
        role=self.cleaned_data.get('role')
        if user.role != role and not user.is_superuser:
            raise ValidationError('Таңдалған рөл сәйкес емес.')
        if user.is_locked():
            raise ValidationError('Аккаунт уақытша бұғатталған. Кейінірек қайта көріңіз.')

class RegisterForm(forms.ModelForm):
    password1=forms.CharField(widget=forms.PasswordInput,label='Құпиясөз')
    password2=forms.CharField(widget=forms.PasswordInput,label='Құпиясөзді қайталаңыз')
    group=forms.CharField(required=False,label='Топ')
    class Meta:
        model=User
        fields=['role','full_name','username']
    def clean(self):
        cleaned=super().clean()
        if cleaned.get('password1') != cleaned.get('password2'):
            raise forms.ValidationError('Құпиясөздер бірдей емес.')
        return cleaned

class ForgotPasswordForm(forms.Form):
    username=forms.CharField(label='Email')

class VerifyCodeForm(forms.Form):
    code=forms.CharField(max_length=6,label='Код (6 сан)')

class ResetPasswordForm(forms.Form):
    password1=forms.CharField(widget=forms.PasswordInput,label='Жаңа құпиясөз')
    password2=forms.CharField(widget=forms.PasswordInput,label='Қайта енгізіңіз')
    def clean(self):
        cleaned=super().clean()
        if cleaned.get('password1') != cleaned.get('password2'):
            raise forms.ValidationError('Құпиясөздер бірдей емес.')
        return cleaned

class GradeForm(forms.ModelForm):
    class Meta:
        model=Grade
        fields=['rk1','rk2','exam','attendance']
        widgets={k: forms.NumberInput(attrs={'min':0,'max':100}) for k in ['rk1','rk2','exam','attendance']}
