from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect

def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request,*args,**kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in roles and not request.user.is_superuser:
                messages.error(request,'Бұл бөлімге қолжетімділік жоқ.')
                return redirect('dashboard')
            return view_func(request,*args,**kwargs)
        return wrapped
    return decorator
