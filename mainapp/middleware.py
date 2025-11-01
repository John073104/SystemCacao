from django.contrib.auth import logout
from firebase_admin import auth as firebase_auth
from django.shortcuts import redirect
from django.contrib.auth import get_user_model as auth_get_user_model
from django.contrib.auth import logout, get_user_model

class FirebaseAuthMiddleware:
    User = auth_get_user_model()
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip for login page
        if request.path == '/login/':
            return self.get_response(request)
            
        # Check Django auth first
        if not request.user.is_authenticated and 'id_token' in request.session:
            try:
                # Verify Firebase token
                decoded_token = firebase_auth.verify_id_token(request.session['id_token'])
                uid = decoded_token['uid']
                
                # Get Django user
                User = get_user_model()
                user = User.objects.get(uid=uid)
                
                # Manually set auth user
                request.user = user
                
            except Exception as e:
                # Invalid token - clear session
                logout(request)
                return redirect('login')
                
        return self.get_response(request)
    
    from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

class SessionSecurityMiddleware(MiddlewareMixin):
    """Middleware to enforce role-based access control (RBAC) and prevent unauthorized URL access"""
    
    # URLs that don't require authentication
    PUBLIC_URLS = [
        '/',
        '/about/',
        '/services/',
        '/team/',
        '/terms/',
        '/privacy/',
        '/login/',
        '/signup/',
        '/forgot-password/',
        '/reset-password/',
        '/unauthorized/',
        '/static/',
        '/media/',
    ]
    
    # URLs that ONLY admins can access
    ADMIN_ONLY_URLS = [
        '/admin/dashboard/',
        '/admin/users/',
        '/admin/ecommerce/',
        '/admin/products/',
        '/admin/orders/',
        '/admin/reports/',
        '/admin/image-analysis/',
        '/admin/farm-location/',
        '/admin/user-management/',
        '/admin/print-preview/',
        '/admin/export-pdf/',
        '/admin/toggle-scan/',
        '/admin/delete-scan/',
        '/admin/export-scan-data/',
    ]
    
    # URLs that users and admins can access
    USER_URLS = [
        '/user/userdashboard/',
        '/user/dashboard/',
        '/dashboard/',
        '/marketplace/',
        '/scan/',
        '/history/',
        '/farm-mapping/',
        '/accounts/',
        '/cart/',
        '/checkout/',
        '/orders/',
        '/profile/',
        '/scan-image/',
        '/scan-history/',
        '/delete-scan-user/',
    ]
    
    # URLs for guest users
    GUEST_URLS = [
        '/guest/dashboard/',
        '/guest/marketplace/',
        '/guest/farm-mapping/',
        '/guest-dashboard/',
        '/guest-scan-image/',
    ]

    def process_request(self, request):
        path = request.path_info
        
        # Skip middleware for public URLs
        if any(path.startswith(url) for url in self.PUBLIC_URLS):
            return None
        
        # Skip middleware for API endpoints
        if path.startswith('/api/'):
            return None
        
        # Get session data
        uid = request.session.get('uid')
        user_email = request.session.get('user_email') or request.session.get('email')
        user_role = request.session.get('role')
        
        # Check if user is authenticated
        if not uid or not user_email:
            messages.error(request, '🔒 Please log in to access this page.')
            return redirect('login')
        
        # SECURITY CHECK 1: Admin-only URLs
        if any(path.startswith(url) for url in self.ADMIN_ONLY_URLS):
            if user_role != 'Admin':
                messages.error(request, '❌ Access Denied: Administrator privileges required.')
                # Redirect based on user role
                if user_role == 'User':
                    return redirect('userdashboard')
                elif user_role == 'Guest':
                    return redirect('guest_dashboard')
                else:
                    return redirect('unauthorized')
        
        # SECURITY CHECK 2: User URLs (Users and Admins can access)
        elif any(path.startswith(url) for url in self.USER_URLS):
            if user_role not in ['User', 'Admin']:
                messages.error(request, '❌ Access Denied: User account required.')
                if user_role == 'Guest':
                    return redirect('guest_dashboard')
                elif user_role == 'Admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect('unauthorized')
        
        # SECURITY CHECK 3: Guest URLs
        elif any(path.startswith(url) for url in self.GUEST_URLS):
            if user_role == 'Admin':
                messages.info(request, 'ℹ️ Redirecting to admin dashboard.')
                return redirect('admin_dashboard')
            elif user_role == 'User':
                messages.info(request, 'ℹ️ Redirecting to user dashboard.')
                return redirect('userdashboard')
        
        return None

class SessionValidationMiddleware(MiddlewareMixin):
    """Middleware to validate session integrity and prevent session tampering"""
    
    def process_request(self, request):
        # Skip validation for public URLs
        public_paths = [
            '/', '/login/', '/signup/', '/about/', '/services/', 
            '/team/', '/terms/', '/privacy/', '/unauthorized/',
            '/forgot-password/', '/reset-password/'
        ]
        
        # Skip static and media files
        if request.path_info.startswith('/static/') or request.path_info.startswith('/media/'):
            return None
            
        if request.path_info in public_paths:
            return None
        
        uid = request.session.get('uid')
        user_email = request.session.get('user_email') or request.session.get('email')
        user_role = request.session.get('role')
        
        # If session claims to be authenticated but missing critical data
        if uid and (not user_email or not user_role):
            # Clear corrupted session
            request.session.flush()
            messages.error(request, '⚠️ Session corrupted or expired. Please log in again.')
            return redirect('login')
        
        # Validate role value
        if user_role and user_role not in ['Admin', 'User', 'Guest']:
            # Invalid role detected - possible session tampering
            request.session.flush()
            messages.error(request, '⚠️ Invalid session detected. Please log in again.')
            return redirect('login')
        
        return None
