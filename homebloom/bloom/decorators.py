from django.shortcuts import redirect
from django.contrib import messages

def user_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_staff:
            return view_func(request, *args, **kwargs)

        messages.error(request, "You are not authorized to access this page.")
        return redirect("login")
    return wrapper

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return view_func(request, *args, **kwargs)

        messages.error(request, "Admin access only.")
        return redirect("login")
    return wrapper