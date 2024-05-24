from functools import wraps
from django.shortcuts import redirect

def login(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('username') and request.session.get('password'):
            return view_func(request, *args, **kwargs)
        else:
            return redirect('login')
    return wrapper