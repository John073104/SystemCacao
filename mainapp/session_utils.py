# ===============================
# SESSION UTILITY FUNCTIONS
# ===============================
from django.shortcuts import redirect
from django.contrib import messages
import jwt
from django.conf import settings

def check_user_session(request):
    """
    Check if user has valid session data
    Returns: (is_authenticated, user_data, redirect_response)
    """
    uid = request.session.get('uid')
    user_email = request.session.get('user_email')
    user_role = request.session.get('role')
    
    if not uid or not user_email:
        return False, None, None
    
    user_data = {
        'uid': uid,
        'email': user_email,
        'name': request.session.get('name', ''),
        'role': user_role or 'User'
    }
    
    return True, user_data, None

def require_login(request, redirect_url='login'):
    """
    Check if user is logged in, redirect if not
    Returns: (is_authenticated, user_data, redirect_response)
    """
    is_auth, user_data, _ = check_user_session(request)
    
    if not is_auth:
        messages.error(request, 'Please log in to access this page.')
        return False, None, redirect(redirect_url)
    
    return True, user_data, None

def require_admin(request):
    """
    Check if user is admin, redirect if not
    Returns: (is_admin, user_data, redirect_response)
    """
    is_auth, user_data, redirect_resp = require_login(request)
    
    if not is_auth:
        return False, None, redirect_resp
    
    if user_data['role'] != 'Admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return False, user_data, redirect('userdashboard')
    
    return True, user_data, None

def require_user_or_admin(request):
    """
    Check if user has User or Admin role
    Returns: (has_access, user_data, redirect_response)
    """
    is_auth, user_data, redirect_resp = require_login(request)
    
    if not is_auth:
        return False, None, redirect_resp
    
    if user_data['role'] not in ['User', 'Admin']:
        messages.error(request, 'Access denied.')
        return False, user_data, redirect('login')
    
    return True, user_data, None

def clear_user_session(request):
    """Clear all user session data"""
    session_keys = ['uid', 'user_email', 'name', 'role', 'checkout_redirect']
    for key in session_keys:
        if key in request.session:
            del request.session[key]
    request.session.modified = True
