from django.core.management.base import BaseCommand
from journal.models import AuditLog, Grade, Group, StudentProfile, Subject, User

class Command(BaseCommand):
    help='Демо деректерді құру'
    def handle(self,*args,**options):
        admin,_=User.objects.get_or_create(username='admin',defaults={'role':User.Roles.ADMIN,'full_name':'System Admin','is_staff':True,'is_superuser':True})
        admin.set_password('Admin12345'); admin.save()
        teacher,_=User.objects.get_or_create(username='teacher1',defaults={'role':User.Roles.TEACHER,'full_name':'Айдос Мұғалім'})
        teacher.set_password('Teacher12345'); teacher.save()
        student,_=User.objects.get_or_create(username='student1',defaults={'role':User.Roles.STUDENT,'full_name':'Сафия Ж'})
        student.set_password('Student12345'); student.save()
        group,_=Group.objects.get_or_create(name='ИС-25')
        StudentProfile.objects.get_or_create(user=student, defaults={'group':group})
        s1,_=Subject.objects.get_or_create(name='Бағдарламалау', teacher=teacher, defaults={'code':'PRG101'})
        s1.groups.add(group)
        s2,_=Subject.objects.get_or_create(name='Математика', teacher=teacher, defaults={'code':'MTH101'})
        s2.groups.add(group)
        g1,_=Grade.objects.get_or_create(student=student, subject=s1, defaults={'rk1':92,'rk2':97,'exam':98,'attendance':94})
        Grade.objects.get_or_create(student=student, subject=s2, defaults={'rk1':88,'rk2':91,'exam':90,'attendance':96})
        AuditLog.objects.get_or_create(user=teacher, action=AuditLog.Actions.UPDATE, entity=f'Grade#{g1.id}', defaults={'old_value':'value: 78','new_value':'value: 88'})
        self.stdout.write(self.style.SUCCESS('Demo data created'))
