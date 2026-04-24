from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
from django.utils import timezone
from .models import AuditLog, User

@receiver(user_logged_in)
def reset_failed_attempts(sender, request, user, **kwargs):
    user.failed_login_attempts=0
    user.locked_until=None
    user.save(update_fields=['failed_login_attempts','locked_until'])
    AuditLog.objects.create(user=user, action=AuditLog.Actions.LOGIN, entity='User login', new_value='Successful login')

@receiver(user_login_failed)
def track_failed_logins(sender, credentials, request, **kwargs):
    username=credentials.get('username')
    if not username: return
    try:
        user=User.objects.get(username=username)
    except User.DoesNotExist:
        return
    user.failed_login_attempts += 1
    if user.failed_login_attempts >= getattr(settings,'LOGIN_LOCK_MAX_ATTEMPTS',5):
        user.locked_until = timezone.now() + timezone.timedelta(minutes=getattr(settings,'LOGIN_LOCK_MINUTES',10))
        user.failed_login_attempts = 0
    user.save(update_fields=['failed_login_attempts','locked_until'])

class LoginAttemptMiddleware:
    def __init__(self,get_response): self.get_response=get_response
    def __call__(self,request): return self.get_response(request)
