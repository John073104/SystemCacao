from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

# --- Helpers ---

def _normalized_role(request):
    """Return normalized (lowercase) role from session."""
    role = request.session.get('role')
    if not role and request.session.get('user_role'):
        role = request.session.get('user_role')
    return str(role or '').strip().lower()


def _is_logged_in(request):
    return bool(request.session.get('uid') and request.session.get('user_email'))


# --- Generic login-required ---

def login_required(view_func):
    """Decorator to require any authenticated user (based on Firebase session)."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not _is_logged_in(request):
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


# --- Role-based decorators ---

def _admin_required(view_func):
    """Allow only admin role."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not _is_logged_in(request):
            messages.error(request, 'Please log in to continue.')
            return redirect('login')
        if _normalized_role(request) != 'admin':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('unauthorized')
        return view_func(request, *args, **kwargs)
    return wrapper

# Backward-compatibility: keep existing name used across code
admin_required = _admin_required


def user_required(view_func):
    """Allow user role and admin role (admins can access user pages)."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not _is_logged_in(request):
            messages.error(request, 'Please log in to continue.')
            return redirect('login')
        role = _normalized_role(request)
        if role not in ['user', 'admin']:
            messages.error(request, 'Access denied. User account required.')
            return redirect('unauthorized')
        return view_func(request, *args, **kwargs)
    return wrapper


def guest_required(view_func):
    """Allow only guest role."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Guests may not have uid/email in session, but we enforce explicit role 'guest'
        role = _normalized_role(request)
        if role != 'guest':
            messages.error(request, 'Access denied. Guest access only.')
            return redirect('unauthorized')
        return view_func(request, *args, **kwargs)
    return wrapper


# --- Anonymous-only decorator ---

def anonymous_required(view_func):
    """Only accessible to non-authenticated users. Authenticated users are redirected based on role."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if _is_logged_in(request):
            role = _normalized_role(request)
            if role == 'admin':
                return redirect('admin_dashboard')
            if role == 'user':
                return redirect('userdashboard')
            if role == 'guest':
                return redirect('guest_dashboard')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper
