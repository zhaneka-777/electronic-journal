import io, random
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from .decorators import role_required
from .forms import ForgotPasswordForm, GradeForm, LoginForm, RegisterForm, ResetPasswordForm, VerifyCodeForm
from .models import AuditLog, Grade, Group, PasswordResetCode, StudentProfile, Subject, User

class CustomLoginView(LoginView):
    template_name='journal/auth/login.html'
    authentication_form=LoginForm
    redirect_authenticated_user=True

def login_view(request):
    return CustomLoginView.as_view()(request)

def register_view(request):
    form=RegisterForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        user=form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        if user.role==User.Roles.ADMIN:
            user.is_staff=True
        user.save()
        group_name=form.cleaned_data.get('group')
        if user.role==User.Roles.STUDENT and group_name:
            group,_=Group.objects.get_or_create(name=group_name)
            StudentProfile.objects.create(user=user, group=group)
        messages.success(request,'Тіркелу сәтті аяқталды.')
        return redirect('login')
    return render(request,'journal/auth/register.html',{'form':form})

def forgot_password_view(request):
    form=ForgotPasswordForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        username=form.cleaned_data['username']
        try:
            user=User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request,'Пайдаланушы табылмады.')
            return render(request,'journal/auth/forgot_password.html',{'form':form})
        code=f"{random.randint(100000,999999)}"
        PasswordResetCode.objects.create(user=user, code=code)
        request.session['reset_user_id']=user.id
        send_mail('Құпиясөзді қалпына келтіру коды', f'Сіздің код: {code}', 'noreply@studentspace.kz', [user.username], fail_silently=True)
        messages.info(request,f'Код жіберілді: {code} (demo режим).')
        return redirect('verify_code')
    return render(request,'journal/auth/forgot_password.html',{'form':form})

def verify_code_view(request):
    form=VerifyCodeForm(request.POST or None)
    code_hint=None
    user_id=request.session.get('reset_user_id')
    if user_id:
        last_code=PasswordResetCode.objects.filter(user_id=user_id).order_by('-created_at').first()
        code_hint=last_code.code if last_code else None
    if request.method=='POST' and form.is_valid():
        code=form.cleaned_data['code']
        record=PasswordResetCode.objects.filter(user_id=user_id,code=code,is_used=False).order_by('-created_at').first()
        if record and record.is_valid():
            request.session['verified_reset_code_id']=record.id
            return redirect('reset_password')
        messages.error(request,'Код қате немесе уақыты өтіп кеткен.')
    return render(request,'journal/auth/verify_code.html',{'form':form,'code_hint':code_hint})

def reset_password_view(request):
    form=ResetPasswordForm(request.POST or None)
    code_id=request.session.get('verified_reset_code_id')
    if not code_id:
        return redirect('forgot_password')
    if request.method=='POST' and form.is_valid():
        record=get_object_or_404(PasswordResetCode,id=code_id,is_used=False)
        user=record.user
        user.set_password(form.cleaned_data['password1'])
        user.save()
        record.is_used=True
        record.save(update_fields=['is_used'])
        messages.success(request,'Құпиясөз жаңартылды.')
        return redirect('login')
    return render(request,'journal/auth/reset_password.html',{'form':form})

@login_required
def dashboard_view(request):
    context={'section':'dashboard'}
    user=request.user
    if user.role==User.Roles.STUDENT:
        grades=list(Grade.objects.filter(student=user).select_related('subject'))
        context.update({
            'today_lessons': grades[:3],
            'average_grade': round(sum(g.final for g in grades)/len(grades),1) if grades else 0,
            'attendance': round(sum(g.attendance for g in grades)/len(grades),1) if grades else 0,
        })
    elif user.role==User.Roles.TEACHER:
        context.update({'subjects': Subject.objects.filter(teacher=user), 'recent_logs': AuditLog.objects.filter(user=user)[:5]})
    else:
        context.update({'users_count': User.objects.count(),'subjects_count': Subject.objects.count(),'grades_count': Grade.objects.count(),'recent_logs': AuditLog.objects.select_related('user')[:8]})
    return render(request,'journal/dashboard.html',context)

@login_required
def grades_view(request):
    grades=Grade.objects.filter(student=request.user).select_related('subject') if request.user.role==User.Roles.STUDENT else Grade.objects.select_related('student','subject')
    return render(request,'journal/grades.html',{'grades':grades,'section':'grades'})

@login_required
@role_required(User.Roles.TEACHER, User.Roles.ADMIN)
def teacher_journal_view(request):
    subjects=Subject.objects.filter(teacher=request.user) if request.user.role==User.Roles.TEACHER else Subject.objects.all()
    selected_subject=request.GET.get('subject')
    selected_group=request.GET.get('group')
    grades=Grade.objects.select_related('student','subject').all()
    if selected_subject: grades=grades.filter(subject_id=selected_subject)
    if selected_group: grades=grades.filter(student__student_profile__group_id=selected_group)
    return render(request,'journal/teacher_journal.html',{'grades':grades,'subjects':subjects,'groups':Group.objects.all(),'selected_subject':selected_subject,'selected_group':selected_group,'section':'teacher_journal'})

@login_required
@role_required(User.Roles.TEACHER, User.Roles.ADMIN)
def edit_grade_view(request, grade_id):
    grade=get_object_or_404(Grade.objects.select_related('subject','student'), id=grade_id)
    if request.user.role==User.Roles.TEACHER and grade.subject.teacher_id != request.user.id:
        messages.error(request,'Тек өз пәніңіздің бағасын өзгерте аласыз.')
        return redirect('teacher_journal')
    old_value=f'rk1={grade.rk1}, rk2={grade.rk2}, exam={grade.exam}, attendance={grade.attendance}'
    form=GradeForm(request.POST or None, instance=grade)
    if request.method=='POST' and form.is_valid():
        grade=form.save()
        new_value=f'rk1={grade.rk1}, rk2={grade.rk2}, exam={grade.exam}, attendance={grade.attendance}'
        AuditLog.objects.create(user=request.user, action=AuditLog.Actions.UPDATE, entity=f'Grade#{grade.id}', old_value=old_value, new_value=new_value)
        messages.success(request,'Баға жаңартылды.')
        return redirect('teacher_journal')
    return render(request,'journal/edit_grade.html',{'form':form,'grade':grade,'section':'teacher_journal'})

@login_required
@role_required(User.Roles.ADMIN)
def audit_log_view(request):
    logs=AuditLog.objects.select_related('user').all()
    search=request.GET.get('search')
    action=request.GET.get('action')
    period=request.GET.get('period')
    if search: logs=logs.filter(Q(entity__icontains=search) | Q(user__username__icontains=search))
    if action: logs=logs.filter(action=action)
    if period=='7': logs=logs.filter(created_at__gte=timezone.now()-timezone.timedelta(days=7))
    elif period=='30': logs=logs.filter(created_at__gte=timezone.now()-timezone.timedelta(days=30))
    return render(request,'journal/audit_log.html',{'logs':logs,'section':'audit_log','action_choices':AuditLog.Actions.choices})

@login_required
def profile_view(request):
    return render(request,'journal/profile.html',{'section':'profile'})

@login_required
def export_excel_view(request):
    wb=Workbook(); ws=wb.active; ws.title='Grades'
    ws.append(['Студент','Пән','РК1','РК2','Емтихан','Қатысу','Қорытынды'])
    grades=Grade.objects.filter(student=request.user) if request.user.role==User.Roles.STUDENT else Grade.objects.all()
    for g in grades.select_related('student','subject'):
        ws.append([g.student.full_name or g.student.username, g.subject.name, g.rk1, g.rk2, g.exam, g.attendance, g.final])
    out=io.BytesIO(); wb.save(out); out.seek(0)
    resp=HttpResponse(out.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    resp['Content-Disposition']='attachment; filename=grades.xlsx'; return resp

@login_required
def export_pdf_view(request):
    buf=io.BytesIO(); pdf=canvas.Canvas(buf, pagesize=A4); width,height=A4
    pdf.setFont('Helvetica-Bold',16); pdf.drawString(50,height-50,'Электрондық журнал есебі')
    grades=Grade.objects.filter(student=request.user) if request.user.role==User.Roles.STUDENT else Grade.objects.all()
    y=height-90; pdf.setFont('Helvetica',10)
    for g in grades.select_related('student','subject')[:25]:
        line=f"{g.student.username} | {g.subject.name} | РК1:{g.rk1} РК2:{g.rk2} Exam:{g.exam} Final:{g.final}"
        pdf.drawString(50,y,line[:100]); y-=18
        if y<60: pdf.showPage(); pdf.setFont('Helvetica',10); y=height-50
    pdf.save(); buf.seek(0)
    resp=HttpResponse(buf, content_type='application/pdf'); resp['Content-Disposition']='attachment; filename=grades_report.pdf'; return resp
