"""
Security Middleware for CacaoGuard System
Prevents role confusion across tabs and unauthorized access
"""
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
import hashlib
import time


class RoleSecurityMiddleware:
    """
    Ensures role consistency across multiple browser tabs.
    Prevents users from accessing admin pages and vice versa.
    Adds security token to prevent session hijacking.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Skip security for public pages
        public_paths = [
            '/login/', '/register/', '/logout/', 
            '/static/', '/media/', '/admin/login/',
            '/', '/home/', '/about/', '/contact/'
        ]
        
        if any(request.path.startswith(path) for path in public_paths):
            return self.get_response(request)
        
        # Check if user has a role
        user_role = request.session.get('role')
        user_email = request.session.get('email')
        
        if not user_role or not user_email:
            # No role set, redirect to login
            if request.path != '/login/':
                messages.warning(request, 'Please login to access this page.')
                return redirect('login')
            return self.get_response(request)
        
        # Generate security token based on role + email + user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        expected_token = hashlib.sha256(
            f"{user_role}{user_email}{user_agent}".encode()
        ).hexdigest()
        
        # Check if security token exists and matches
        stored_token = request.session.get('security_token')
        if not stored_token:
            # First time, set the token
            request.session['security_token'] = expected_token
            request.session['token_created_at'] = time.time()
        elif stored_token != expected_token:
            # Token mismatch - possible session hijacking or role change
            messages.error(request, 'Security error: Session invalid. Please login again.')
            request.session.flush()
            return redirect('login')
        
        # Check role-based access
        is_admin_path = request.path.startswith('/admin/') and not request.path.startswith('/admin/login/')
        is_user_path = request.path.startswith('/user/')
        is_guest_path = request.path.startswith('/guest/')
        
        # Enforce role-based access
        if user_role == 'admin':
            if is_user_path or is_guest_path:
                messages.error(request, 'Admin cannot access user/guest pages. Please use admin dashboard.')
                return redirect('admin_dashboard')
        elif user_role == 'user':
            if is_admin_path or is_guest_path:
                messages.error(request, 'Users cannot access admin/guest pages.')
                return redirect('userdashboard')
        elif user_role == 'guest':
            if is_admin_path or is_user_path:
                messages.error(request, 'Guests cannot access admin/user pages.')
                return redirect('guest_dashboard')
        
        # Token refresh every 1 hour
        token_age = time.time() - request.session.get('token_created_at', 0)
        if token_age > 3600:  # 1 hour
            request.session['security_token'] = expected_token
            request.session['token_created_at'] = time.time()
        
        response = self.get_response(request)
        
        # Add security headers
        response['X-Frame-Options'] = 'DENY'
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response


class CSRFProtectionMiddleware:
    """
    Enhanced CSRF protection for sensitive operations
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Check for suspicious requests
        if request.method == 'POST':
            # Verify referer for POST requests
            referer = request.META.get('HTTP_REFERER', '')
            host = request.META.get('HTTP_HOST', '')
            
            if referer and host not in referer:
                messages.error(request, 'Security error: Invalid request origin.')
                return redirect('home')
        
        return self.get_response(request)


class SessionTimeoutMiddleware:
    """
    Automatic session timeout for inactive users
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.timeout = 3600  # 1 hour in seconds
        
    def __call__(self, request):
        if request.session.get('email'):
            last_activity = request.session.get('last_activity')
            current_time = time.time()
            
            if last_activity:
                if current_time - last_activity > self.timeout:
                    request.session.flush()
                    messages.info(request, 'Your session has expired. Please login again.')
                    return redirect('login')
            
            request.session['last_activity'] = current_time
        
        return self.get_response(request)
