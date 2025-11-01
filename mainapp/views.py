from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .firebase_config import auth
import requests
import time
import jwt
from functools import wraps
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .decorators import admin_required, user_required


FIREBASE_WEB_API_KEY = 'AIzaSyAs90apE9AG6k4aIg9MpJD750OsvVD70m4'
SECRET_KEY = '49qVayZTdlh0rkFE8uxB0mh6IrdILzk8s0v1z0UZ'

from django.shortcuts import render, redirect
from django.contrib import messages
from firebase_admin import auth, firestore
import requests, jwt

# Firestore instance - will be initialized when needed
# Import firebase_config to ensure Firebase is initialized
from . import firebase_config
db = firebase_config.db if hasattr(firebase_config, 'db') and firebase_config.db else None

from django.contrib.auth import login
# from django.contrib.auth.models import User

from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import messages
import requests
from firebase_admin import auth
import jwt
from .models import CustomUser
from django.contrib.auth import get_user_model
User = get_user_model()


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            # 🔐 Sign in using Firebase REST API
            api_key = 'AIzaSyAs90apE9AG6k4aIg9MpJD750OsvVD70m4'
            payload = {
                'email': email,
                'password': password,
                'returnSecureToken': True
            }
            r = requests.post(
                f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}',
                data=payload
            )
            r.raise_for_status()
            res = r.json()
            id_token = res['idToken']
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']

            # ✅ Fetch additional user data from Firestore
            user_docs = db.collection('users').where('email', '==', email).stream()
            user_data = None
            for doc in user_docs:
                user_data = doc.to_dict()
                break

            if not user_data:
                messages.error(request, 'User record not found in Firestore.')
                return redirect('login')

            # 🧠 Store important session values
            request.session['uid'] = uid
            request.session['name'] = user_data.get('name', '')
            request.session['user_email'] = user_data.get('email', '')
            role_value = str(user_data.get('role', 'user')).strip().lower()
            request.session['role'] = role_value  # normalized to 'admin' | 'user' | 'guest'
            
            # Save session explicitly
            request.session.save()
            
            # Debug output
            print(f"Login successful - UID: {uid}")
            print(f"Session after login: {dict(request.session)}")

            # 🪪 Issue JWT and redirect based on role/checkout intent
            token = jwt.encode({'uid': uid, 'role': request.session['role']}, SECRET_KEY, algorithm='HS256')
            
            # Check if user was trying to checkout
            if request.session.get('checkout_redirect'):
                # Remove the checkout redirect flag
                del request.session['checkout_redirect']
                request.session.modified = True
                
                response = redirect('checkout_view')
                response.set_cookie('session', token)
                messages.success(request, f'Welcome back, {user_data.get("name", "User")}! You can now proceed with checkout.')
                return response
            
            # Regular login redirect based on role (normalized lowercase)
            response = redirect('admin_dashboard' if request.session['role'] == 'admin' else 'userdashboard')
            response.set_cookie('session', token)
            messages.success(request, f'Welcome back, {user_data.get("name", "User")}!')

            return response

        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error during login: {e}")
            messages.error(request, 'Invalid credentials.')
        except Exception as e:
            print(f"Login error: {e}")
            messages.error(request, f'Login failed: {e}')

    return render(request, 'accounts/login.html')


# Create a simple authentication decorator for your views
def firebase_login_required(view_func):
    """Decorator to require Firebase authentication"""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('uid') or not request.session.get('user_email'):
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


# Example usage of the decorator:
@user_required
def user_dashboard(request):
    """User dashboard view"""
    context = {
        'user_name': request.session.get('name'),
        'user_email': request.session.get('user_email'),
        'user_role': request.session.get('role')
    }
    return render(request, 'user/userdashboard.html', context)


@admin_required
def admin_dashboard(request):
    """Admin dashboard view"""
    # Check if user is actually admin (normalized lowercase)
    if request.session.get('role') != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('userdashboard')
    
    context = {
        'user_name': request.session.get('name'),
        'user_email': request.session.get('user_email')
    }
    return render(request, 'admin/dashboard.html', context)
# ===============================
# SIGNUP VIEW
# ===============================
def signup_view(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']

        try:
            # Create user in Firebase
            user = auth.create_user_with_email_and_password(email, password)
            uid = user['localId']

            # Save user info in Firebase Database
            role = 'user'
            db.child("users").child(uid).set({
                "email": email,
                "name": name,
                "role": role
            })

            # ✅ Success message with email
            messages.success(request, f"You are registered with {email}. You can now sign in.")
            return redirect('login')

        except Exception as e:
            error_msg = str(e)
            if "EMAIL_EXISTS" in error_msg:
                messages.error(request, "Email already exists.")
            else:
                messages.error(request, "Signup failed. Please try again.")
            return redirect('signup')

    return render(request, "accounts/signup.html")

# ===============================
#  Admin Dashboard
# ===============================
from .decorators import admin_required, user_required
from .firebase_config import db

@admin_required
def admin_dashboard(request):
    print("[DEBUG] Accessing Admin Dashboard:", request.session.get('email'), request.session.get('role'))
    user_list = []
    try:
        users_ref = db.collection('users')
        users_docs = users_ref.stream()
        for doc in users_docs:
            data = doc.to_dict()
            user_list.append({
                'uid': doc.id,
                'name': data.get('name', 'N/A'),
                'email': data.get('email', 'N/A'),
                'role': data.get('role', 'N/A')
            })
    except Exception as e:
        print("[ERROR] Failed to fetch users:", str(e))
        messages.error(request, "Failed to load users.")

    context = {
        'name': request.session.get('name'),
        'email': request.session.get('email'),
        'role': request.session.get('role'),
        'users': user_list,
        'user_count': len(user_list)
    }
    return render(request, 'admin/admin_dashboard.html', context)

# ===============================
# User Dashboard
# ===============================
@user_required
def userdashboard(request):
    print("[DEBUG] Accessing User Dashboard:", request.session.get('email'), request.session.get('role'))

    if request.session.get('role') == 'guest':
        messages.error(request, "Guest users cannot access user dashboard.")
        return redirect('guest_dashboard')

    context = {
        'name': request.session.get('name'),
        'email': request.session.get('email'),
        'role': request.session.get('role')
    }
    return render(request, 'user/userdashboard.html', context)


def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            auth.send_password_reset_email(email)
            messages.success(request, "Password reset link sent to your email.")
            return redirect('login')
        except:
            messages.error(request, "Error sending password reset email.")
            return redirect('forgot_password')
    return render(request, 'accounts/forgot_password.html')

from django.shortcuts import render

def custom_403(request, exception=None):
    return render(request, '403.html', status=403)

# ===============================
# FORGOT PASSWORD
# ===============================
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            auth.send_password_reset_email(email)
            messages.success(request, "Password reset link sent to your email.")
            return redirect('login')
        except:
            messages.error(request, "Error sending password reset email.")
            return redirect('forgot_password')
    return render(request, 'accounts/forgot_password.html')


# ===============================
# LOGOUT
# ===============================
def logout_view(request):
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect('login')


# ===============================
# Landing Page
# ===============================
def home(request): return render(request, 'home.html')
def about(request): return render(request, 'about.html')
def services(request): return render(request, 'services.html')
def team(request): return render(request, 'team.html')

def unauthorized(request):
    return render(request, 'unauthorized.html')


def firebase_login(request):
    return redirect('login')

from django.http import JsonResponse
from django.core.mail import send_mail

def send_welcome_email(request):
    try:
        recipient = request.GET.get('to')
        send_mail(
            'Welcome to CacaoGuard!',
            'Thanks for signing up to our platform.',
            'jardinesjohnlloyd@gmail.com', 
            [recipient],
            fail_silently=False,
        )
        return JsonResponse({'status': 'Email sent'})
    except Exception as e:
        return JsonResponse({'status': 'Failed to send email', 'error': str(e)}, status=500)


def image_analysis(request):
    return render(request, 'admin/image_analysis.html')

def ecommerce(request):
    return render(request, 'admin/ecommerce.html')
@admin_required
def farm_location(request):
    return render(request, 'admin/farm_location_fixed.html')


# Scan and Diagnose view
def scan_diagnose(request):
    context = {
        'page_title': 'Scan and Diagnose',
        'description': 'Upload crop images for disease detection and analysis'
    }
    return render(request, 'user/scan_diagnose.html', context)

# Marketplace view
def marketplace(request):
    context = {
        'page_title': 'Marketplace',
        'description': 'Buy and sell agricultural products'
    }
    return render(request, 'user/marketplace.html', context)

# Farm Mapping view
@user_required
def farm_mapping(request):
    context = {
        'page_title': 'Farm Mapping',
        'description': 'View and manage detailed maps of your farm'
    }
    return render(request, 'user/farm_mapping.html', context)

# Accounts and Orders view
def accounts(request):
    context = {
        'page_title': 'Accounts',
        'description': 'Manage your account'
    }
    return render(request, 'user/accounts.html', context)

from .decorators import guest_required
@guest_required
def guest_dashboard(request):
    if 'uid' not in request.session or request.session.get('role') != 'guest':
        messages.error(request, "Access denied.")
        return redirect('login')
        
    context = {
        'name': request.session.get('name'),
        'email': request.session.get('email'),
        'role': request.session.get('role')
    }
    return render(request, 'guest/guest_dashboard.html', context)


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout


# Guest pages
@guest_required
def guest_dashboard(request):
    return render(request, 'guest/guest_dashboard.html') 

def guest_marketplace(request):
    return render(request, 'guest/guest_marketplace.html')

def guest_farm_mapping(request):
    return render(request, 'guest/guest_farmMapping.html')


# ===============================
# Image Procesing
# ===============================

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .firebase_config import auth
import requests
import time
import jwt
from functools import wraps
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .decorators import admin_required, user_required, guest_required, anonymous_required

import json
from datetime import datetime, timedelta
import uuid
import os
import numpy as np
from PIL import Image
import firebase_admin
from firebase_admin import credentials, firestore, storage
from google.cloud.firestore_v1.base_query import FieldFilter
from django.utils import timezone
from django.core.paginator import Paginator
import pytz
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import resnet18
import logging
import traceback
import random
from django.utils import timezone as django_timezone
from datetime import timezone as datetime_timezone

# Initialize Firebase Admin SDK
# Path to your Firebase service account key
cred_path = os.path.join(settings.BASE_DIR, 'systemcacao-firebase-adminsdk-fbsvc-126c1bf0e1.json')
if not firebase_admin._apps:
    if os.path.exists(cred_path):
# Firebase and Firestore already initialized in firebase_config
# Just use the db from there (already imported at top of file)

# Global variables for models
disease_model = None
pest_model = None

# Set up logging
logger = logging.getLogger(__name__)

FIREBASE_WEB_API_KEY = 'AIzaSyAs90apE9AG6k4aIg9MpJD750OsvVD70m4'
SECRET_KEY = '49qVayZTdlh0rkFE8uxB0mh6IrdILzk8s0v1z0UZ'


# ===============================
# PYTORCH MODEL LOADING AND PREPROCESSING
# ===============================

class CacaoResNet(nn.Module):
    def __init__(self, num_classes):
        super(CacaoResNet, self).__init__()
        self.resnet = resnet18(pretrained=False)
        self.resnet.fc = nn.Linear(self.resnet.fc.in_features, num_classes)
    
    def forward(self, x):
        return self.resnet(x)

import torch

def load_pytorch_model(model_path, model_class, num_classes):
    try:
        model = model_class(num_classes=num_classes)
        state_dict = torch.load(model_path, map_location="cpu")

        # Fix key mismatch by adding "resnet." prefix if missing
        new_state_dict = {}
        for k, v in state_dict.items():
            if not k.startswith("resnet."):
                new_state_dict["resnet." + k] = v
            else:
                new_state_dict[k] = v

        model.load_state_dict(new_state_dict, strict=False)
        model.eval()
        print(f"Successfully loaded PyTorch model: {model_path}")
        return model
    except Exception as e:
        print(f"Error loading PyTorch model {model_path}: {e}")
        return None


# Load your models (PyTorch only)
# Both trained with 5 classes
disease_model = load_pytorch_model(
    "models/cacao_disease_resnet_state_dict.pth", CacaoResNet, num_classes=5
)
pest_model = load_pytorch_model(
    "models/cacao_pest_resnet_state_dict.pth", CacaoResNet, num_classes=5
)

# Disease and Pest classes
DISEASE_CLASSES = [
    'Black Pod Rot',
    'Fito Disease',
    'Monilia Disease',
    'Healthy',
    'Frosty Pod Rot',
    'Witches Broom',
    'Unknown'
]

PEST_CLASSES = [
    'Ant Weaver',
    'Aphids',
    'Mealybug',
    'Pod Borer',
    'Healthy',
    'Unknown'
]


# Recommendations
DISEASE_RECOMMENDATIONS = {
    'Black Pod Rot': [
        'Remove and destroy infected pods immediately',
        'Improve drainage and air circulation',
        'Apply copper-based fungicides',
        'Harvest ripe pods promptly'
    ],
    'Fito Disease': [
        'Improve soil drainage and reduce waterlogging',
        'Remove and destroy infected plant parts',
        'Apply recommended fungicides as preventive measure',
        'Monitor plants regularly for new symptoms'
    ],
    'Monilia Disease': [
        'Remove infected pods and plant debris',
        'Prune to improve air circulation',
        'Apply protective fungicides during wet season',
        'Plant resistant varieties when available'
    ],
    'Frosty Pod Rot': [
        'Remove and destroy infected pods promptly',
        'Sanitize tools after pruning',
        'Apply copper fungicides during wet seasons',
        'Maintain proper field sanitation'
    ],
    'Witches Broom': [
        'Prune infected branches 30cm below symptoms',
        'Remove all brooms and infected tissue',
        'Apply copper fungicides as preventive treatment',
        'Maintain good farm hygiene and weed control'
    ],
    'Healthy': [
        'Continue current management practices',
        'Regular monitoring for early detection',
        'Maintain proper nutrition and irrigation',
        'Keep farm clean and well-maintained'
    ],
    'Unknown': [
        'Monitor affected plants closely for symptom progression',
        'Consult local agricultural expert for accurate diagnosis',
        'Avoid unnecessary chemical applications',
        'Document and report unusual symptoms for research'
    ]
}

PEST_RECOMMENDATIONS = {
    'Ant Weaver': [
        'Locate and destroy ant nests around plantation',
        'Trim branches touching each other to prevent ant movement',
        'Use baiting techniques with approved insecticides',
        'Encourage natural predators of ants'
    ],
    'Aphids': [
        'Encourage natural predators like lady beetles',
        'Use reflective mulches to repel aphids',
        'Apply insecticidal soap or neem oil',
        'Remove heavily infested shoots'
    ],
    'Mealybug': [
        'Introduce natural enemies such as parasitoids',
        'Apply systemic insecticides only if severe',
        'Maintain ant control to reduce mealybug spread',
        'Regularly monitor and intervene early'
    ],
    'Pod Borer': [
        'Harvest pods every 7-10 days to break pest cycle',
        'Remove and destroy infested pods immediately',
        'Install pheromone traps to monitor population',
        'Apply biological control agents such as Trichogramma'
    ],
    'Healthy': [
        'Continue integrated pest management',
        'Regular monitoring for early detection',
        'Maintain beneficial insect populations',
        'Keep plantation clean and well-managed'
    ],
    'Unknown': [
        'Collect samples for proper identification',
        'Avoid immediate pesticide application until confirmed',
        'Monitor population levels over several days',
        'Seek expert assistance if pest persists'
    ]
}


def preprocess_image_pytorch(image_file):
    """Preprocess image for PyTorch model"""
    try:
        # Open image
        if hasattr(image_file, 'read'):
            image = Image.open(image_file).convert('RGB')
        else:
            image = Image.open(image_file).convert('RGB')
        
        # Define transforms
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # Apply transforms and add batch dimension
        image_tensor = transform(image).unsqueeze(0)
        return image_tensor
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        raise

# ===============================
# SCAN AND DIAGNOSE VIEWS
# ===============================

def scan_diagnose(request):
    """User scan diagnose view"""
    context = {
        'uid': request.session.get('uid'),
        'user_email': request.session.get('user_email'),
        'role': request.session.get('role', 'user')
    }
    return render(request, 'user/scan_diagnose.html', context)

def guest_scan_diagnose(request):
    """Guest scan diagnose view"""
    today = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d')
    session_key = f'guest_limits_{today}'

    if session_key not in request.session:
        request.session[session_key] = {'disease': 0, 'pest': 0}

    context = {
        'daily_limits': request.session[session_key],
        'max_daily_scans': 5,
        'today': today
    }
    return render(request, 'guest/guest_scan_diagnose.html', context)

import hashlib

def _get_image_hash(image_file):
    """Generate a hash for the image to detect duplicates"""
    import hashlib
    image_file.seek(0)  # Reset file pointer
    content = image_file.read()
    return hashlib.md5(content).hexdigest()

def _is_duplicate_scan(user_id, image_hash):
    """Check if the same image has been scanned before"""
    try:
        # Check in Firebase for existing scans with same hash
        scans_ref = db.collection('scans')
        query = scans_ref.where('user_id', '==', user_id).where('image_hash', '==', image_hash)
        docs = list(query.stream())
        return len(docs) > 0
    except Exception:
        return False

def simulate_analysis(scan_type, image_file=None):
    """Simulate ML analysis with deterministic results based on image hash"""
    classes, recommendations = (
        (DISEASE_CLASSES, DISEASE_RECOMMENDATIONS) if scan_type == 'disease' 
        else (PEST_CLASSES, PEST_RECOMMENDATIONS)
    )
    
    # Generate deterministic result based on image content
    if image_file:
        try:
            # Reset file pointer to beginning
            image_file.seek(0)
            # Create hash of image content
            image_hash = hashlib.md5(image_file.read()).hexdigest()
            # Reset file pointer again for later use
            image_file.seek(0)
            
            # Use hash to deterministically select class and confidence
            hash_int = int(image_hash[:8], 16)
            class_index = hash_int % len(classes)
            result_class = classes[class_index]
            
            # Generate deterministic confidence (75-98%)
            confidence = 0.75 + ((hash_int % 23) / 100.0)
        except Exception as e:
            print(f"Error hashing image: {e}")
            # Fallback to random
            result_class = random.choice(classes)
            confidence = random.uniform(0.75, 0.98)
    else:
        # Fallback to random if no image provided
        result_class = random.choice(classes)
        confidence = random.uniform(0.75, 0.98)
    
    return {
        'class': result_class,
        'confidence': confidence,
        'recommendations': recommendations.get(result_class, [])
    }

@csrf_exempt
def scan_image(request):
    """Handle image scanning for both users and guests"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

    try:
        scan_type = request.POST.get('scan_type', 'disease')
        image_file = request.FILES.get('image')
        if not image_file:
            return JsonResponse({'success': False, 'message': 'No image provided'})

        # Default guest
        user_type, user_id, user_email, user_name = 'guest', 'guest', 'guest@example.com', 'Guest User'

        if request.session.get('uid'):
            user_type = 'user'
            user_id = request.session.get('uid')
            user_email = request.session.get('user_email', '')
            user_name = request.session.get('name', 'User')
        else:
            # Guest scan limits
            today = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d')
            session_key = f'guest_limits_{today}'
            if session_key not in request.session:
                request.session[session_key] = {'disease': 0, 'pest': 0}
            daily_limits = request.session[session_key]
            if daily_limits.get(scan_type, 0) >= 5:
                return JsonResponse({
                    'success': False,
                    'message': f'Daily {scan_type} scan limit reached (5/5). Please sign up for unlimited scans.'
                })

        # Check for duplicate image (prevent scanning same image multiple times)
        image_hash = _get_image_hash(image_file)
        if _is_duplicate_scan(user_id, image_hash):
            return JsonResponse({
                'success': False,
                'message': 'This image has already been scanned. Please upload a different image.',
                'duplicate': True
            })

        # Simulate scan
        analysis_result = simulate_analysis(scan_type, image_file)
        scan_id = str(uuid.uuid4())

        scan_data = {
            'scan_id': scan_id,
            'user_id': user_id,
            'user_email': user_email,
            'user_name': user_name,
            'user_type': user_type,
            'type': scan_type,
            'result': analysis_result['class'],
            'confidence': analysis_result['confidence'],
            'recommendations': analysis_result['recommendations'],
            'image_name': image_file.name,
            'image_hash': image_hash,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'hidden': False
        }

        # Save to Firestore
        try:
            doc_ref = db.collection('scans').document(scan_id)
            doc_ref.set(scan_data)
            print(f"[DEBUG] Scan saved to Firestore with ID: {scan_id}")
        except Exception as firestore_error:
            print(f"[ERROR] Failed to save to Firestore: {firestore_error}")
            # Continue without Firestore if it fails

        if user_type == 'guest':
            request.session[session_key][scan_type] += 1
            request.session.modified = True
            remaining_scans = {
                'disease': max(0, 5 - request.session[session_key].get('disease', 0)),
                'pest': max(0, 5 - request.session[session_key].get('pest', 0))
            }
        else:
            remaining_scans = {'disease': 'unlimited', 'pest': 'unlimited'}

        return JsonResponse({
            'success': True,
            'scan_id': scan_id,
            'type': scan_type,
            'result': analysis_result['class'],
            'confidence': round(analysis_result['confidence'] * 100, 2),
            'recommendations': analysis_result['recommendations'],
            'remaining_scans': remaining_scans
        })
    except Exception as e:
        print(f"Error in scan_image: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Error processing scan: {str(e)}'})

def get_scan_history(request):
    """Get scan history for current user/guest"""
    try:
        uid = request.session.get('uid')
        if not uid:
            return JsonResponse({'success': True, 'scans': []})

        print(f"[DEBUG] Fetching scan history for user: {uid}")

        # Get user's scans from Firestore
        scans_ref = db.collection('scans').where('user_id', '==', uid).order_by('timestamp', direction=firestore.Query.DESCENDING)
        scans = []

        for doc in scans_ref.stream():
            scan_data = doc.to_dict()
            scan_data['id'] = doc.id

            # Preserve original timestamp format
            if 'timestamp' in scan_data and scan_data['timestamp']:
                if hasattr(scan_data['timestamp'], 'seconds'):
                    scan_data['timestamp'] = {
                        'seconds': scan_data['timestamp'].seconds,
                        'nanoseconds': getattr(scan_data['timestamp'], 'nanoseconds', 0)
                    }
                elif isinstance(scan_data['timestamp'], str):
                    pass  # Keep original ISO string
                else:
                    scan_data['timestamp'] = scan_data['timestamp'].isoformat()
            else:
                scan_data['timestamp'] = scan_data.get('created_at', None)

            scans.append(scan_data)

        print(f"[DEBUG] Found {len(scans)} scans for user {uid}")
        return JsonResponse({'success': True, 'scans': scans})
    except Exception as e:
        print(f"[ERROR] Error getting scan history: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
def delete_user_scan(request, scan_id):
    """Delete user's scan"""
    if request.method == 'POST':
        try:
            uid = request.session.get('uid')
            if not uid:
                return JsonResponse({'success': False, 'error': 'Authentication required'})
            
            scan_ref = db.collection('scans').document(scan_id)
            scan_doc = scan_ref.get()
            
            if not scan_doc.exists:
                return JsonResponse({'success': False, 'error': 'Scan not found'})
            
            scan_data = scan_doc.to_dict()
            
            if scan_data.get('user_id') != uid:
                return JsonResponse({'success': False, 'error': 'Unauthorized'})
            
            scan_ref.delete()
            print(f"[DEBUG] Scan {scan_id} deleted by user {uid}")
            
            return JsonResponse({'success': True, 'message': 'Scan deleted successfully'})
            
        except Exception as e:
            print(f"[ERROR] Error deleting scan: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# ===============================
# Scan End
# ===============================

# ===============================
# Marketplace
# ===============================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from decimal import Decimal
import json
import uuid
import os
import uuid
from .models import Product, Category, Cart, CartItem, Order, OrderItem
from .firebase_utils import firestore_service



# User
@user_required
def marketplace(request):
    """User marketplace view"""
    # Get filter parameters
    category = request.GET.get('category')
    product_type = request.GET.get('type')
    search = request.GET.get('search')
    sort_by = request.GET.get('sort', 'name')
    
    # Get products from Firestore
    products = firestore_service.get_products()
    
    # Filter products
    if category:
        products = [p for p in products if p.get('category') == category]
    
    if product_type:
        products = [p for p in products if p.get('product_type') == product_type]
    
    if search:
        products = [p for p in products if search.lower() in p.get('name', '').lower() or 
                   search.lower() in p.get('description', '').lower()]
    
    # Sort products
    if sort_by == 'price_low':
        products.sort(key=lambda x: x.get('price', 0))
    elif sort_by == 'price_high':
        products.sort(key=lambda x: x.get('price', 0), reverse=True)
    elif sort_by == 'newest':
        products.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    # Get categories for filter
    categories = list(set([p.get('category') for p in products if p.get('category')]))
    
    # Get user's cart count from session
    cart_count = 0
    if request.user.is_authenticated:
        cart = request.session.get('cart', [])
        cart_count = sum(item['quantity'] for item in cart)
    
    context = {
        'products': products,
        'categories': categories,
        'cart_count': cart_count,
        'current_category': category,
        'current_type': product_type,
        'current_search': search,
        'current_sort': sort_by,
        'product_types': [
            ('fresh_cacao', 'Fresh Cacao Fruit'),
            ('dried_beans', 'Dried Cacao Beans'),
            ('cacao_powder', 'Cacao Powder'),
            ('chocolate', 'Chocolate Products'),
            ('cacao_butter', 'Cacao Butter'),
            ('cacao_nibs', 'Cacao Nibs'),
        ]
    }
    
    return render(request, 'user/marketplace.html', context)

@user_required
def product_detail(request, product_id):
    """Product detail view"""
    product = firestore_service.get_product(product_id)
    if not product:
        messages.error(request, 'Product not found.')
        return redirect('marketplace')
    
    # Get related products
    related_products = firestore_service.get_products(limit=4)
    related_products = [p for p in related_products if p.get('id') != product_id][:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    
    return render(request, 'user/product_detail.html', context)

from django.shortcuts import get_object_or_404, redirect
@user_required
@csrf_exempt
def add_to_cart(request):
    """Add product to cart using session storage"""
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        
        # Get product from Firestore
        product_data = firestore_service.get_product(product_id)
        if not product_data:
            return JsonResponse({'success': False, 'message': 'Product not found'})
        
        # Check stock
        if quantity > product_data.get('stock_quantity', 0):
            return JsonResponse({'success': False, 'message': 'Insufficient stock'})
        
        # Get cart from session
        cart = request.session.get('cart', [])
        
        # Check if product already in cart
        product_found = False
        for item in cart:
            if item['product_id'] == product_id:
                item['quantity'] += quantity
                product_found = True
                break
        
        if not product_found:
            cart.append({
                'product_id': product_id,
                'quantity': quantity
            })
        
        # Save cart to session
        request.session['cart'] = cart
        request.session.modified = True
        
        # Calculate cart count
        cart_count = sum(item['quantity'] for item in cart)
        
        return JsonResponse({
            'success': True, 
            'message': 'Product added to cart',
            'cart_count': cart_count
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def checkout_view(request):
    """Checkout process with Firebase session authentication"""
    
    # Check Firebase authentication using session data
    uid = request.session.get('uid')
    user_email = request.session.get('user_email')
    user_name = request.session.get('name')
    user_role = request.session.get('role')
    
    # Debug output
    print(f"UID: {uid}")
    print(f"Email: {user_email}")
    print(f"Name: {user_name}")
    print(f"Role: {user_role}")
    print(f"Session data: {dict(request.session)}")
    
    # Check if user is authenticated (has Firebase session data)
    if not uid or not user_email:
        messages.error(request, 'Please log in to proceed with checkout.')
        # Store the current URL to redirect back after login
        request.session['checkout_redirect'] = True
        return redirect('login')
    
    cart_items_data = request.session.get('cart', [])
    
    if not cart_items_data:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart_view')
    
    # Get detailed cart items
    cart_items = []
    total_amount = 0
    
    for item_data in cart_items_data:
        try:
            product_data = firestore_service.get_product(item_data['product_id'])
            if product_data:
                item_total = float(product_data.get('price', 0)) * item_data['quantity']
                cart_items.append({
                    'product': product_data,
                    'quantity': item_data['quantity'],
                    'total_price': item_total
                })
                total_amount += item_total
        except Exception as e:
            print(f"Error getting product {item_data['product_id']}: {str(e)}")
            continue
    
    if not cart_items:
        messages.error(request, 'Unable to load cart items. Please try again.')
        return redirect('cart_view')
    
    if request.method == 'POST':
        # Process order
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        shipping_address = request.POST.get('shipping_address', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        notes = request.POST.get('notes', '').strip()
        payment_method = request.POST.get('payment_method', 'cod')
        
        # Pre-fill email with logged-in user's email if not provided
        if not email:
            email = user_email
        
        # Validate required fields
        if not all([first_name, last_name, email, shipping_address, phone_number]):
            messages.error(request, 'Please fill in all required fields.')
            context = {
                'cart_items': cart_items,
                'total': total_amount,
                'user_name': user_name,
                'user_email': user_email,
                'form_data': {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'shipping_address': shipping_address,
                    'phone_number': phone_number,
                    'notes': notes,
                    'payment_method': payment_method
                }
            }
            return render(request, 'user/checkout.html', context)
        
        try:
            # Double-check user is still authenticated before creating order
            if not request.session.get('uid'):
                messages.error(request, 'Session expired. Please log in again.')
                return redirect('login')
            
            # Generate unique order ID
            import uuid
            from datetime import datetime
            
            order_id = str(uuid.uuid4())[:8].upper()  # Short order ID
            
            # Prepare order items data
            order_items_data = []
            for item in cart_items:
                order_items_data.append({
                    'product_id': item['product']['id'],
                    'product_name': item['product']['name'],
                    'quantity': item['quantity'],
                    'price': float(item['product']['price']),
                    'total_price': item['total_price']
                })
            
            # Create order data for Firestore
            order_data = {
                'order_id': order_id,
                'firebase_uid': uid,
                'customer_first_name': first_name,
                'customer_last_name': last_name,
                'customer_email': email,
                'customer_name': user_name,
                'status': 'pending',
                'total_amount': float(total_amount),
                'shipping_address': shipping_address,
                'phone_number': phone_number,
                'notes': notes,
                'payment_method': payment_method,
                'items': order_items_data,
                'created_at': firestore.SERVER_TIMESTAMP,
                'order_date': datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Save order to Firestore
            firestore_service.add_order(order_data)
            
            # Clear cart
            request.session['cart'] = []
            request.session.modified = True
            
            # Store order ID in session for confirmation page
            request.session['last_order_id'] = order_id
            
            messages.success(request, f'Order placed successfully! Order ID: {order_id}')
            
            # Redirect to order confirmation
            return redirect('order_confirmation', order_id=order_id)
            
        except Exception as e:
            print(f"Order creation error: {str(e)}")
            messages.error(request, f'Error processing order: {str(e)}')
            context = {
                'cart_items': cart_items,
                'total': total_amount,
                'user_name': user_name,
                'user_email': user_email,
                'form_data': {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'shipping_address': shipping_address,
                    'phone_number': phone_number,
                    'notes': notes,
                    'payment_method': payment_method
                }
            }
            return render(request, 'user/checkout.html', context)
    
    # Pre-fill form with user data
    form_data = {
        'email': user_email,
        'first_name': user_name.split(' ')[0] if user_name else '',
        'last_name': ' '.join(user_name.split(' ')[1:]) if user_name and len(user_name.split(' ')) > 1 else ''
    }
    
    context = {
        'cart_items': cart_items,
        'total': total_amount,
        'user_name': user_name,
        'user_email': user_email,
        'user_role': user_role,
        'form_data': form_data
    }
    
    return render(request, 'user/checkout.html', context)

import logging

logger = logging.getLogger(__name__)

@user_required
def order_confirmation(request, order_id):
    """Order confirmation page"""
    try:
        uid = request.session.get('uid')
        user_email = request.session.get('user_email') or request.session.get('email')
        if not uid or not user_email:
            messages.error(request, 'Please log in to view your order.')
            return redirect('login')

        orders_ref = db.collection('orders')
        query = orders_ref.where('order_id', '==', order_id).limit(1)
        docs = list(query.stream())
        if not docs:
            messages.error(request, 'Order not found.')
            return redirect('user_orders')

        doc = docs[0]
        order_data = doc.to_dict()
        order_data['id'] = doc.id

        # Check ownership using firebase_uid or customer_email fallback
        owner_uid = order_data.get('firebase_uid') or order_data.get('user_id')
        owner_email = order_data.get('customer_email') or order_data.get('user_email')
        if owner_uid and owner_uid != uid and owner_email and owner_email != user_email:
            messages.error(request, 'Access denied.')
            return redirect('userdashboard')

        # Convert timestamp to Asia/Manila if Firestore timestamp
        if order_data.get('created_at') and hasattr(order_data['created_at'], 'seconds'):
            utc_time = datetime.fromtimestamp(order_data['created_at'].seconds, tz=pytz.UTC)
            philippines_tz = pytz.timezone('Asia/Manila')
            order_data['created_at'] = utc_time.astimezone(philippines_tz)

        # Items are stored inline on the order document
        order_items = order_data.get('items', [])

        context = {
            'order': order_data,
            'order_items': order_items,
            'order_id': order_id,
            'user_name': request.session.get('name'),
            'user_email': user_email,
            'payment_status': order_data.get('payment_status', 'pending')
        }
        return render(request, 'user/order_confirmation.html', context)

    except Exception as e:
        logger.exception("Order confirmation error")
        messages.error(request, 'Error loading order details.')
        return redirect('userdashboard')

def logout_view(request):
    """Logout view"""
    
    # Clear all session data
    request.session.flush()
    
    # Create response and clear cookies
    response = redirect('login')
    response.delete_cookie('session')
    
    messages.success(request, 'You have been logged out successfully.')
    return response


# Add this to your firestore_service.py if not already present
class FirestoreService:
    def __init__(self):
        # Your existing firestore initialization
        pass
    
    def get_order_by_id(self, order_id):
        """Get order by order ID"""
        try:
            orders_ref = db.collection('orders')
            query = orders_ref.where('order_id', '==', order_id).limit(1)
            docs = query.stream()
            
            for doc in docs:
                return doc.to_dict()
            
            return None
        except Exception as e:
            print(f"Error getting order: {str(e)}")
            return None
    
    def add_order(self, order_data):
        """Add order to Firestore"""
        try:
            doc_ref = db.collection('orders').add(order_data)
            return doc_ref[1].id  # Return document ID
        except Exception as e:
            print(f"Error adding order: {str(e)}")
            raise e


@user_required
def cart_view(request):
    """View cart"""
    # Get cart items from session (simplified approach for Firestore integration)
    cart_items = request.session.get('cart', [])
    
    # Fetch product details from Firestore for each cart item
    detailed_cart_items = []
    total = 0
    
    for item in cart_items:
        product_data = firestore_service.get_product(item['product_id'])
        if product_data:
            item_total = float(product_data.get('price', 0)) * item['quantity']
            detailed_cart_items.append({
                'product': product_data,
                'quantity': item['quantity'],
                'total_price': item_total
            })
            total += item_total
    
    context = {
        'cart_items': detailed_cart_items,
        'total': total,
    }
    
    return render(request, 'user/cart.html', context)


import uuid
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from .models import Order, OrderItem, CartItem, Product
from decimal import Decimal

# Removed duplicate user_orders function - keeping the most complete version at line 10221


@user_required
def order_detail(request, order_id):
    """Order detail view (Firestore)"""
    try:
        uid = request.session.get('uid')
        user_email = request.session.get('user_email') or request.session.get('email')
        if not uid:
            messages.error(request, 'Please log in to view your order.')
            return redirect('login')

        # Try by document ID first
        order_ref = db.collection('orders').document(order_id)
        doc = order_ref.get()

        if not doc.exists:
            # Fallback by human-friendly order_id field
            q = db.collection('orders').where('order_id', '==', order_id).limit(1)
            docs = list(q.stream())
            if not docs:
                messages.error(request, 'Order not found.')
                return redirect('user_orders')
            doc = docs[0]

        order = doc.to_dict()
        order['id'] = doc.id

        # Ownership check
        owner_uid = order.get('firebase_uid') or order.get('user_id')
        owner_email = order.get('customer_email') or order.get('user_email')
        if owner_uid and owner_uid != uid and owner_email and owner_email != user_email:
            messages.error(request, 'Access denied.')
            return redirect('user_orders')

        # Convert timestamp
        if order.get('created_at') and hasattr(order['created_at'], 'seconds'):
            order['created_at'] = datetime.fromtimestamp(order['created_at'].seconds, tz=pytz.UTC).astimezone(pytz.timezone('Asia/Manila'))

        # Ensure items list exists
        order.setdefault('items', [])

        return render(request, 'user/order_detail.html', {'order': order})
    except Exception:
        logger.exception('Error loading order detail')
        messages.error(request, 'Error loading order details.')
        return redirect('user_orders')

@user_required
@csrf_exempt
def update_cart_item(request):
    """Update cart item quantity"""
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        
        cart = request.session.get('cart', [])
        
        for item in cart:
            if item['product_id'] == product_id:
                if quantity <= 0:
                    cart.remove(item)
                else:
                    item['quantity'] = quantity
                break
        
        request.session['cart'] = cart
        request.session.modified = True
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@user_required
@csrf_exempt
def remove_from_cart(request):
    """Remove item from cart"""
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        cart = request.session.get('cart', [])
        cart = [item for item in cart if item['product_id'] != product_id]
        
        request.session['cart'] = cart
        request.session.modified = True
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

# Admin Views
def is_admin(user):
    return user.is_staff or user.is_superuser

@admin_required
def admin_ecommerce(request):
    """Admin ecommerce dashboard with Firestore data"""
    try:
        # ===== ORDERS SECTION =====
        orders_ref = db.collection('orders')
        all_orders_docs = list(orders_ref.stream())
        
        total_orders = len(all_orders_docs)
        pending_orders = 0
        total_revenue = 0
        recent_orders_data = []
        
        for doc in all_orders_docs:
            order_data = doc.to_dict()
            order_data['id'] = doc.id
            
            # Count pending orders
            if order_data.get('status') == 'pending':
                pending_orders += 1
            
            # Calculate revenue
            if order_data.get('status') == 'delivered':
                total_revenue += float(order_data.get('total_amount', 0))
            
            # Format timestamp
            if 'created_at' in order_data:
                if hasattr(order_data['created_at'], 'seconds'):
                    order_data['created_at'] = datetime.fromtimestamp(order_data['created_at'].seconds, tz=pytz.UTC).astimezone(pytz.timezone('Asia/Manila'))
                else:
                    order_data['created_at'] = order_data['created_at']
            else:
                order_data['created_at'] = datetime.now(pytz.timezone('Asia/Manila'))
            
            # Structure user data
            order_data['user'] = {
                'email': order_data.get('customer_email', 'No email'),
                'first_name': order_data.get('customer_first_name', ''),
                'last_name': order_data.get('customer_last_name', ''),
                'username': order_data.get('customer_email', 'user').split('@')[0]
            }
            
            recent_orders_data.append(order_data)
        
        # Get 5 most recent orders
        recent_orders = sorted(
            recent_orders_data,
            key=lambda x: x['created_at'],
            reverse=True
        )[:5]

        # ===== PRODUCTS SECTION =====
        # Get ALL products from Firestore
        products_ref = db.collection('products')
        all_products = [doc.to_dict() for doc in products_ref.stream()]
        
        total_products = len(all_products)
        low_stock_products = [
            p for p in all_products 
            if p.get('stock_quantity', 0) <= 5
        ]

        context = {
            # Core metrics
            'total_products': total_products,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'total_revenue': round(total_revenue, 2),
            
            # Lists
            'recent_orders': recent_orders,
            'low_stock_products': low_stock_products,
            
            # Full datasets (if needed in template)
            'all_products': all_products,
        }

        return render(request, 'admin/ecommerce.html', context)

    except Exception as e:
        print(f"ERROR in admin_ecommerce: {str(e)}")
        # Fallback empty data
        return render(request, 'admin/ecommerce.html', {
            'total_products': 0,
            'total_orders': 0,
            'pending_orders': 0,
            'total_revenue': 0,
            'recent_orders': [],
            'low_stock_products': [],
        })
    
@admin_required
def admin_products(request):
    """Admin products management"""
    products = firestore_service.get_products(active_only=False)
    
    # Add pagination
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
    }
    
    return render(request, 'admin/products.html', context)

def handle_uploaded_images(image_files):
    """Handle uploaded image files and return their URLs"""
    image_urls = []
    
    for image_file in image_files:
        # Generate unique filename
        file_extension = os.path.splitext(image_file.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Save to media/products/ folder
        file_path = f"products/{unique_filename}"
        saved_path = default_storage.save(file_path, ContentFile(image_file.read()))
        
        # Get the URL for the saved file
        file_url = default_storage.url(saved_path)
        image_urls.append(file_url)
    
    return image_urls

@admin_required
def admin_add_product(request):
    """Add new product"""
    if request.method == 'POST':
        # Handle file uploads
        images = []
        if request.FILES.getlist('images'):
            images = handle_uploaded_images(request.FILES.getlist('images'))

        product_data = {
            'name': request.POST.get('name'),
            'description': request.POST.get('description'),
            'category': request.POST.get('category'),
            'product_type': request.POST.get('product_type'),
            'price': float(request.POST.get('price')),
            'stock_quantity': int(request.POST.get('stock_quantity')),
            'unit': request.POST.get('unit'),
            'origin': request.POST.get('origin', ''),
            'is_active': request.POST.get('is_active') == 'on',
            'featured': request.POST.get('featured') == 'on',
            'images': images,
        }
        
        # Add harvest date if provided
        harvest_date = request.POST.get('harvest_date')
        if harvest_date:
            product_data['harvest_date'] = harvest_date
        
        product_id = firestore_service.add_product(product_data)
        
        messages.success(request, 'Product added successfully!')
        return redirect('admin_products')
    
    context = {
        'product_types': [
            ('fresh_cacao', 'Fresh Cacao Fruit'),
            ('dried_beans', 'Dried Cacao Beans'),
            ('cacao_powder', 'Cacao Powder'),
            ('chocolate', 'Chocolate Products'),
            ('cacao_butter', 'Cacao Butter'),
            ('cacao_nibs', 'Cacao Nibs'),
        ]
    }
    
    return render(request, 'admin/add_product.html', context)

@admin_required
def admin_edit_product(request, product_id):
    """Edit product"""
    product = firestore_service.get_product(product_id)
    if not product:
        messages.error(request, 'Product not found.')
        return redirect('admin_products')
    
    if request.method == 'POST':
        update_data = {
            'name': request.POST.get('name'),
            'description': request.POST.get('description'),
            'category': request.POST.get('category'),
            'product_type': request.POST.get('product_type'),
            'price': float(request.POST.get('price')),
            'stock_quantity': int(request.POST.get('stock_quantity')),
            'unit': request.POST.get('unit'),
            'origin': request.POST.get('origin', ''),
            'is_active': request.POST.get('is_active') == 'on',
            'featured': request.POST.get('featured') == 'on',
        }
        
        # Handle new image uploads if provided
        if request.FILES.getlist('images'):
            images = handle_uploaded_images(request.FILES.getlist('images'))
            update_data['images'] = images
        
        # Handle harvest date
        harvest_date = request.POST.get('harvest_date')
        if harvest_date:
            update_data['harvest_date'] = harvest_date
        
        firestore_service.update_product(product_id, update_data)
        
        messages.success(request, 'Product updated successfully!')
        return redirect('admin_products')
    
    context = {
        'product': product,
        'product_types': [
            ('fresh_cacao', 'Fresh Cacao Fruit'),
            ('dried_beans', 'Dried Cacao Beans'),
            ('cacao_powder', 'Cacao Powder'),
            ('chocolate', 'Chocolate Products'),
            ('cacao_butter', 'Cacao Butter'),
            ('cacao_nibs', 'Cacao Nibs'),
        ]
    }
    
    return render(request, 'admin/edit_product.html', context)

@admin_required
def admin_delete_product(request, product_id):
    """Delete product"""
    if request.method == 'POST':
        # Get product to delete associated images
        product = firestore_service.get_product(product_id)
        if product and product.get('images'):
            # Delete associated image files
            for image_url in product['images']:
                try:
                    # Extract file path from URL
                    file_path = image_url.replace('/media/', '')
                    if default_storage.exists(file_path):
                        default_storage.delete(file_path)
                except Exception as e:
                    print(f"Error deleting image: {e}")
        
        firestore_service.delete_product(product_id)
        messages.success(request, 'Product deleted successfully!')
    
    return redirect('admin_products')

def admin_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'admin/orders.html', {'orders': orders})

# admin report
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
import pytz
from firebase_admin import firestore
import json
from calendar import monthrange

# Initialize Firestore
PHILIPPINES_TZ = pytz.timezone('Asia/Manila')




@admin_required
@require_http_methods(["POST"])
def update_order_status(request, order_id):
    """Update order status with stock deduction and email notifications"""
    try:
        order_ref = db.collection('orders').document(order_id)
        order_doc = order_ref.get()
        
        if not order_doc.exists:
            return JsonResponse({'success': False, 'message': 'Order not found'})
        
        order_data = order_doc.to_dict()
        old_status = order_data.get('status')
        new_status = request.POST.get('status')
        
        # Update order status in Firebase
        order_ref.update({
            'status': new_status,
            'updated_at': datetime.now(pytz.timezone('Asia/Manila')),
            'updated_by': request.session.get('admin_email', 'admin')
        })
        
        # Deduct stock when order is delivered (only if status changed to delivered)
        if new_status == 'delivered' and old_status != 'delivered':
            deduct_stock_for_order(order_data)
        
        # Send email notification
        send_status_change_email(order_data, new_status)
        
        return JsonResponse({'success': True, 'message': f'Order status updated to {new_status}'})
        
    except Exception as e:
        print(f"Error updating order status: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)})

def deduct_stock_for_order(order_data):
    """Deduct stock quantities when order is delivered"""
    try:
        products_ref = db.collection('products')
        
        for item in order_data.get('items', []):
            product_id = item.get('product_id')
            quantity_ordered = int(item.get('quantity', 0))
            
            if not product_id:
                continue
                
            # Get current product data
            product_ref = products_ref.document(product_id)
            product_doc = product_ref.get()
            
            if product_doc.exists:
                product_data = product_doc.to_dict()
                current_stock = int(product_data.get('stock_quantity', 0))
                new_stock = max(0, current_stock - quantity_ordered)
                
                # Update stock in Firebase
                product_ref.update({
                    'stock_quantity': new_stock,
                    'last_updated': datetime.now(pytz.timezone('Asia/Manila'))
                })
                
                print(f"Stock updated for {product_data.get('name', 'Unknown Product')}: {current_stock} -> {new_stock}")
            else:
                print(f"Product {product_id} not found for stock deduction")
                
    except Exception as e:
        print(f"Error deducting stock: {str(e)}")

def send_status_change_email(order_data, new_status):
    """Send email notification when order status changes"""
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        # Get customer email
        customer_email = order_data.get('customer_email') or order_data.get('user_email')
        order_id = order_data.get('order_id', 'N/A')
        customer_name = order_data.get('customer_first_name', 'Customer')
        
        if not customer_email:
            print("No customer email found for notification")
            return
            
        # Email content based on status
        status_messages = {
            'confirmed': {
                'subject': f'Order #{order_id} Confirmed',
                'message': f'Hi {customer_name},\n\nYour order #{order_id} has been confirmed and is being prepared for processing.\n\nThank you for your purchase!'
            },
            'processing': {
                'subject': f'Order #{order_id} Being Processed',
                'message': f'Hi {customer_name},\n\nYour order #{order_id} is now being processed and will be shipped soon.\n\nThank you for your patience!'
            },
            'shipped': {
                'subject': f'Order #{order_id} Shipped',
                'message': f'Hi {customer_name},\n\nGreat news! Your order #{order_id} has been shipped and is on its way to you.\n\nThank you for your purchase!'
            },
            'delivered': {
                'subject': f'Order #{order_id} Delivered',
                'message': f'Hi {customer_name},\n\nYour order #{order_id} has been successfully delivered!\n\nWe hope you enjoy your cacao products. Thank you for choosing us!'
            }
        }
        
        if new_status in status_messages:
            email_data = status_messages[new_status]
            
            send_mail(
                subject=email_data['subject'],
                message=email_data['message'],
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@cacaomarketplace.com'),
                recipient_list=[customer_email],
                fail_silently=True,
            )
            
            print(f"Email sent to {customer_email} for order {order_id} status: {new_status}")
        else:
            print(f"No email template for status: {new_status}")
            
    except Exception as e:
        print(f"Error sending email notification: {str(e)}")

from django.shortcuts import render
from django.http import JsonResponse
from firebase_admin import firestore
import firebase_admin
from firebase_admin import credentials
from datetime import datetime, timedelta
import pytz
from collections import defaultdict
import calendar

# Firebase is already initialized in firebase_config.py
# No need to initialize again here
from .firebase_config import db

USD_TO_PHP_RATE = 56.0  # 1 USD = 56 PHP (adjust as needed)

def get_customer_name(user_email):
    """Fetch customer name from users collection"""
    try:
        users_ref = db.collection('users')
        user_query = users_ref.where('email', '==', user_email).limit(1)
        users = list(user_query.stream())
        
        if users:
            user_data = users[0].to_dict()
            # Try different name field combinations
            name = (user_data.get('full_name') or 
                   user_data.get('name') or 
                   f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip() or
                   user_email.split('@')[0])
            return name
        return user_email.split('@')[0]  # Fallback to email username
    except Exception as e:
        print(f"[DEBUG] Error fetching customer name for {user_email}: {str(e)}")
        return user_email.split('@')[0]

def admin_reports(request):
    """Generate admin reports with proper error handling"""
    try:
        # Get current date in Philippines timezone
        philippines_tz = pytz.timezone('Asia/Manila')
        now = datetime.now(philippines_tz)
        current_year = now.year
        current_month = now.month
        
        print(f"[DEBUG] Fetching reports for {current_year}-{current_month}")
        
        # Fetch all orders from Firestore
        orders_ref = db.collection('orders')
        all_orders = list(orders_ref.stream())  # Convert to list to ensure all data is fetched
        
        print(f"[DEBUG] Total orders in database: {len(all_orders)}")
        
        # Process orders
        monthly_orders = []
        total_orders = 0
        delivered_orders = 0
        pending_orders = 0
        total_revenue = 0
        
        # For charts
        daily_sales = defaultdict(float)
        product_sales = defaultdict(int)
        
        for order_doc in all_orders:
            total_orders += 1
            order_data = order_doc.to_dict()
            
            try:
                order_timestamp = None
                
                timestamp_fields = ['timestamp', 'created_at', 'order_date', 'date_created', 'createdAt']
                for field in timestamp_fields:
                    if field in order_data and order_data[field] is not None:
                        timestamp_value = order_data[field]
                        
                        try:
                            # Handle different timestamp formats
                            if hasattr(timestamp_value, 'timestamp'):
                                # Firestore timestamp
                                order_timestamp = datetime.fromtimestamp(timestamp_value.timestamp(), tz=philippines_tz)
                            elif isinstance(timestamp_value, str):
                                # String timestamp - try multiple formats
                                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']:
                                    try:
                                        if 'T' in timestamp_value:
                                            timestamp_value = timestamp_value.replace('Z', '')
                                        order_timestamp = datetime.strptime(timestamp_value, fmt)
                                        order_timestamp = philippines_tz.localize(order_timestamp)
                                        break
                                    except:
                                        continue
                            elif isinstance(timestamp_value, (int, float)):
                                # Unix timestamp
                                if timestamp_value > 1e10:  # Milliseconds
                                    timestamp_value = timestamp_value / 1000
                                order_timestamp = datetime.fromtimestamp(timestamp_value, tz=philippines_tz)
                            
                            if order_timestamp:
                                break
                        except Exception as e:
                            print(f"[DEBUG] Error parsing timestamp field {field}: {str(e)}")
                            continue
                
                if not order_timestamp:
                    print(f"[DEBUG] No valid timestamp found for order {order_doc.id}, using current time")
                    order_timestamp = now
                
                if (order_timestamp.year == current_year and 
                    order_timestamp.month == current_month):
                    
                    user_email = order_data.get('user_email', order_data.get('email', 'N/A'))
                    customer_name = get_customer_name(user_email)
                    
                    amount_usd = float(order_data.get('total_amount', 0))
                    amount_php = amount_usd * USD_TO_PHP_RATE
                    
                    order_info = {
                        'id': order_doc.id,
                        'order_id': order_data.get('order_id', order_doc.id),
                        'user_email': user_email,
                        'customer_name': customer_name,  # Added customer name
                        'total_amount': amount_php,  # Amount in PHP
                        'total_amount_usd': amount_usd,  # Keep USD for reference
                        'status': order_data.get('status', 'pending').lower(),
                        'timestamp': order_timestamp,
                        'items': order_data.get('items', [])
                    }
                    
                    monthly_orders.append(order_info)
                    
                    # Update metrics
                    if order_info['status'] in ['delivered', 'completed', 'shipped']:
                        delivered_orders += 1
                        total_revenue += amount_php  # Revenue in PHP
                        
                        # Add to daily sales for chart
                        day_key = order_timestamp.strftime('%Y-%m-%d')
                        daily_sales[day_key] += amount_php
                    elif order_info['status'] in ['pending', 'processing', 'confirmed']:
                        pending_orders += 1
                    
                    # Count product sales
                    for item in order_info['items']:
                        if isinstance(item, dict):
                            product_name = item.get('name', item.get('product_name', 'Unknown'))
                            quantity = int(item.get('quantity', 1))
                            product_sales[product_name] += quantity
                            
            except Exception as e:
                print(f"[DEBUG] Error processing order {order_doc.id}: {str(e)}")
                continue
        
        print(f"[DEBUG] Monthly orders found: {len(monthly_orders)}")
        print(f"[DEBUG] Metrics - Total: {len(monthly_orders)}, Delivered: {delivered_orders}, Pending: {pending_orders}, Revenue: ₱{total_revenue:,.2f}")
        
        # Prepare chart data
        chart_dates = []
        chart_sales = []
        
        # Generate all days in current month
        for day in range(1, calendar.monthrange(current_year, current_month)[1] + 1):
            date_key = f"{current_year}-{current_month:02d}-{day:02d}"
            chart_dates.append(f"{current_month}/{day}")
            chart_sales.append(daily_sales.get(date_key, 0))
        
        # Top products
        top_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]
        
        monthly_orders.sort(key=lambda x: x['timestamp'], reverse=True)
        
        context = {
            'total_orders': len(monthly_orders),
            'delivered_orders': delivered_orders,
            'pending_orders': pending_orders,
            'total_revenue': total_revenue,
            'monthly_orders': monthly_orders,
            'top_products': top_products,
            'chart_dates': chart_dates,
            'chart_sales': chart_sales,
            'current_month': calendar.month_name[current_month],
            'current_year': current_year,
        }
        
        print("[DEBUG] Context prepared successfully")
        return render(request, 'admin/reports.html', context)
        
    except Exception as e:
        print(f"[ERROR] Failed to generate reports: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return empty context to prevent template errors
        context = {
            'total_orders': 0,
            'delivered_orders': 0,
            'pending_orders': 0,
            'total_revenue': 0,
            'monthly_orders': [],
            'top_products': [],
            'chart_dates': [],
            'chart_sales': [],
            'current_month': calendar.month_name[datetime.now().month],
            'current_year': datetime.now().year,
            'error_message': f"Error loading reports: {str(e)}"
        }
        return render(request, 'admin/reports.html', context)

def print_monthly_report(request, year, month):
    """Generate printable monthly report"""
    try:
        print(f"[DEBUG] Generating print report for {year}-{month}")
        
        # Philippines timezone
        philippines_tz = pytz.timezone('Asia/Manila')
        
        # Fetch orders (same logic as admin_reports but for specific month/year)
        orders_ref = db.collection('orders')
        all_orders = list(orders_ref.stream())  # Convert to list to ensure all data is fetched
        
        monthly_orders = []
        total_revenue = 0
        delivered_orders = 0
        
        for order_doc in all_orders:
            order_data = order_doc.to_dict()
            
            try:
                order_timestamp = None
                
                timestamp_fields = ['timestamp', 'created_at', 'order_date', 'date_created', 'createdAt']
                for field in timestamp_fields:
                    if field in order_data and order_data[field] is not None:
                        timestamp_value = order_data[field]
                        
                        try:
                            if hasattr(timestamp_value, 'timestamp'):
                                order_timestamp = datetime.fromtimestamp(timestamp_value.timestamp(), tz=philippines_tz)
                            elif isinstance(timestamp_value, str):
                                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']:
                                    try:
                                        if 'T' in timestamp_value:
                                            timestamp_value = timestamp_value.replace('Z', '')
                                        order_timestamp = datetime.strptime(timestamp_value, fmt)
                                        order_timestamp = philippines_tz.localize(order_timestamp)
                                        break
                                    except:
                                        continue
                            elif isinstance(timestamp_value, (int, float)):
                                if timestamp_value > 1e10:
                                    timestamp_value = timestamp_value / 1000
                                order_timestamp = datetime.fromtimestamp(timestamp_value, tz=philippines_tz)
                            
                            if order_timestamp:
                                break
                        except:
                            continue
                
                if not order_timestamp:
                    continue
                
                # Check if order is in specified month/year
                if (order_timestamp.year == year and 
                    order_timestamp.month == month):
                    
                    user_email = order_data.get('user_email', order_data.get('email', 'N/A'))
                    customer_name = get_customer_name(user_email)
                    amount_usd = float(order_data.get('total_amount', 0))
                    amount_php = amount_usd * USD_TO_PHP_RATE
                    
                    order_info = {
                        'id': order_doc.id,
                        'order_id': order_data.get('order_id', order_doc.id),
                        'user_email': user_email,
                        'customer_name': customer_name,
                        'total_amount': amount_php,
                        'status': order_data.get('status', 'pending').lower(),
                        'timestamp': order_timestamp,
                        'items': order_data.get('items', [])
                    }
                    
                    monthly_orders.append(order_info)
                    
                    if order_info['status'] in ['delivered', 'completed', 'shipped']:
                        delivered_orders += 1
                        total_revenue += amount_php
                        
            except Exception as e:
                print(f"[DEBUG] Error processing order for print: {str(e)}")
                continue
        
        monthly_orders.sort(key=lambda x: x['timestamp'], reverse=True)
        
        context = {
            'monthly_orders': monthly_orders,
            'total_revenue': total_revenue,
            'delivered_orders': delivered_orders,
            'total_orders': len(monthly_orders),
            'month_name': calendar.month_name[month],
            'year': year,
            'report_date': datetime.now(philippines_tz).strftime('%B %d, %Y')
        }
        
        return render(request, 'admin/print_monthly_report.html', context)
        
    except Exception as e:
        print(f"[ERROR] Failed to generate print report: {str(e)}")
        context = {
            'monthly_orders': [],
            'total_revenue': 0,
            'delivered_orders': 0,
            'total_orders': 0,
            'month_name': calendar.month_name[month],
            'year': year,
            'report_date': datetime.now().strftime('%B %d, %Y'),
            'error_message': f"Error loading report: {str(e)}"
        }
        return render(request, 'admin/print_monthly_report.html', context)



@admin_required
def admin_pending_orders(request):
    """Show only pending orders"""
    try:
        orders_ref = db.collection('orders')
        pending_orders_query = orders_ref.where('status', '==', 'pending')
        pending_orders = list(pending_orders_query.stream())
        
        orders_data = []
        for doc in pending_orders:
            order_data = doc.to_dict()
            order_data['id'] = doc.id
            
            if 'created_at' in order_data and order_data['created_at']:
                if hasattr(order_data['created_at'], 'seconds'):
                    utc_time = datetime.fromtimestamp(order_data['created_at'].seconds, tz=pytz.UTC)
                    order_data['created_at'] = utc_time.astimezone(PHILIPPINES_TZ)
            
            orders_data.append(order_data)
        
        context = {
            'orders': orders_data,
            'filter_type': 'pending',
            'total_orders': len(orders_data)
        }
        
        return render(request, 'admin/orders.html', context)
        
    except Exception as e:
        print(f"Error in admin_pending_orders: {str(e)}")
        return redirect('admin_ecommerce')

@admin_required
def admin_order_detail(request, order_id):
    """View detailed order information"""
    try:
        order_ref = db.collection('orders').document(order_id)
        order_doc = order_ref.get()
        
        if not order_doc.exists:
            messages.error(request, "Order not found.")
            return redirect('admin_orders')
        
        order_data = order_doc.to_dict()
        order_data['id'] = order_doc.id
        
        # Convert timestamp
        if 'created_at' in order_data and order_data['created_at']:
            if hasattr(order_data['created_at'], 'seconds'):
                utc_time = datetime.fromtimestamp(order_data['created_at'].seconds, tz=pytz.UTC)
                order_data['created_at'] = utc_time.astimezone(PHILIPPINES_TZ)
        
        # Calculate totals
        total_items = sum(item.get('quantity', 0) for item in order_data.get('items', []))
        order_data['total_items'] = total_items
        
        for item in order_data.get('items', []):
            item['total_price'] = float(item.get('price', 0)) * int(item.get('quantity', 0))
        
        context = {'order': order_data}
        return render(request, 'admin/order_detail.html', context)
        
    except Exception as e:
        print(f"Error in admin_order_detail: {str(e)}")
        messages.error(request, "Error loading order details.")
        return redirect('admin_orders')

@admin_required
def admin_orders(request):
    """Display all orders with filtering"""
    try:
        status_filter = request.GET.get('status', 'all')
        
        orders_ref = db.collection('orders')
        if status_filter != 'all':
            orders_query = orders_ref.where('status', '==', status_filter)
        else:
            orders_query = orders_ref
            
        all_orders = list(orders_query.stream())
        
        orders_data = []
        for doc in all_orders:
            order_data = doc.to_dict()
            order_data['id'] = doc.id
            
            if 'created_at' in order_data and order_data['created_at']:
                if hasattr(order_data['created_at'], 'seconds'):
                    utc_time = datetime.fromtimestamp(order_data['created_at'].seconds, tz=pytz.UTC)
                    order_data['created_at'] = utc_time.astimezone(PHILIPPINES_TZ)
            
            total_items = sum(item.get('quantity', 0) for item in order_data.get('items', []))
            order_data['total_items'] = total_items
            
            orders_data.append(order_data)
        
        orders_data.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
        
        context = {
            'orders': orders_data,
            'status_filter': status_filter,
            'total_orders': len(orders_data),
        }
        
        return render(request, 'admin/orders.html', context)
        
    except Exception as e:
        print(f"Error in admin_orders: {str(e)}")
        return redirect('admin_ecommerce')

# views.py
from django.shortcuts import render
from .models import Order
from django.core.paginator import Paginator
from .decorators import admin_required  # if you're using a custom decorator

@admin_required
def admin_orders(request):
    status_filter = request.GET.get('status')

    orders = Order.objects.all()
    if status_filter:
        orders = orders.filter(status=status_filter)

    orders = orders.order_by('-created_at')

    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj,
        'status_choices': Order.STATUS_CHOICES,
        'current_status': status_filter,
    }

    return render(request, 'admin/orders.html', context)

@admin_required
def admin_order_detail(request, order_id):
    """Admin order detail"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            
            # Update in Firestore as well
            firestore_service.update_order_status(str(order.id), new_status)
            
            messages.success(request, f'Order status updated to {new_status}')
    
    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    }
    
    return render(request, 'admin/order_detail.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def shipping_info(request):
    if request.method == 'POST':
        request.session['shipping_address'] = request.POST.get('shipping_address')
        request.session['phone_number'] = request.POST.get('phone_number')
        return redirect('payment')
    return render(request, 'checkout/shipping.html')



def payment(request):
    if request.method == 'POST':
        request.session['payment_method'] = request.POST.get('payment_method')
        return redirect('confirm_order')
    return render(request, 'checkout/payment.html')



def confirm_order(request):
    shipping_address = request.session.get('shipping_address')
    phone_number = request.session.get('phone_number')
    payment_method = request.session.get('payment_method')

    if request.method == 'POST':
        # ✅ Place order logic here (adjust to match your Order model)
        from .models import Order  # Make sure your Order model is imported
        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            phone_number=phone_number,
            status='pending',
            total_amount=0  # Replace with real amount
        )

        # ✅ Optional: Clean session after placing order
        request.session.pop('shipping_address', None)
        request.session.pop('phone_number', None)
        request.session.pop('payment_method', None)

        messages.success(request, "Order placed successfully!")
        return redirect('user_orders')

    context = {
        'shipping_address': shipping_address,
        'phone_number': phone_number,
        'payment_method': payment_method
    }
    return render(request, 'checkout/confirm.html', context)

# ===============================
# Marketplace End
# ===============================


from django.contrib.auth import logout as auth_logout


def logout_view(request):
    """Custom logout view"""
    auth_logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')


#June
# Updated views for the farm mapping system

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .decorators import admin_required, user_required, guest_required
import json

# Sample farm data - replace with your database/Firebase integration
SAMPLE_FARMS = [
    {
        'id': 1,
        'name': 'Barangay Poblacion Farm',
        'municipality': 'Victoria',
        'barangay': 'Poblacion',
        'area': 4.5,
        'trees': 10,
        'status': 'Active',
        'lat': 13.1375,
        'lng': 121.2410,
        'description': 'Primary cacao growing area with established farms',
        'contact': 'Brgy. Captain Juan Santos',
        'created_at': '2024-01-15',
        'images': [
            '/static/images/download (2).jpg',
            '/static/images/download (1).jpg',
            '/static/images/download (3).jpg'
        ]

    },
    {
        'id': 2,
        'name': 'San Vicente Cacao Farm',
        'municipality': 'Victoria',
        'barangay': 'San Vicente',
        'area': 3.2,
        'trees': 15,
        'status': 'Active',
        'lat': 13.1500,
        'lng': 121.2333,
        'description': 'Emerging farming community with modern techniques',
        'contact': 'Brgy. Captain Maria Cruz',
        'created_at': '2024-01-14',
        'images': [
            '/static/images/download (1).jpg',
            '/static/images/download.jpg'
        ]
    },
    {
        'id': 3,
        'name': 'Macatoc Cacao Farm',
        'municipality': 'Victoria',
        'barangay': 'Macatoc',
        'area': 8.5,
        'trees': 13,
        'status': 'Monitoring',
        'lat': 13.1440,
        'lng': 121.2320,
        'description': 'Large scale cacao production facility',
        'contact': 'Farm Manager Pedro Reyes',
        'created_at': '2024-01-13',
        'images': [
            '/static/images/download (3).jpg',
            '/static/images/download (2).jpg'
        ]
    }
]

@admin_required
def farm_location(request):
    """Admin farm management view with CRUD and analytics"""
    context = {
        'page_title': 'Farm Management',
        'farms_data': SAMPLE_FARMS,
        'total_farms': len(SAMPLE_FARMS),
        'total_area': sum(farm['area'] for farm in SAMPLE_FARMS),
        'total_trees': sum(farm['trees'] for farm in SAMPLE_FARMS),
        'municipalities': list(set(farm['municipality'] for farm in SAMPLE_FARMS))
    }
    return render(request, 'admin/farm_location_fixed.html', context)

@user_required
def farm_mapping(request):
    """User farm mapping view with interactive features"""
    context = {
        'page_title': 'Farm Mapping',
        'description': 'Explore and interact with farm data',
        'farms_data': SAMPLE_FARMS,
        'user_name': request.session.get('name', 'User'),
        'user_role': request.session.get('role', 'User')
    }
    return render(request, 'user/farm_mapping.html', context)

def guest_farm_mapping(request):
    """Guest farm mapping view - read-only access"""
    # Filter data for public viewing (remove sensitive information)
    public_farms = []
    for farm in SAMPLE_FARMS:
        public_farm = {
            'id': farm['id'],
            'name': farm['name'],
            'municipality': farm['municipality'],
            'barangay': farm['barangay'],
            'area': farm['area'],
            'trees': farm['trees'],
            'status': farm['status'],
            'lat': farm['lat'],
            'lng': farm['lng'],
            'description': farm['description']
            # Exclude contact and other sensitive info
        }
        public_farms.append(public_farm)
    
    context = {
        'farms_data': public_farms,
        'total_farms': len(public_farms),
        'total_area': sum(farm['area'] for farm in public_farms),
        'total_trees': sum(farm['trees'] for farm in public_farms)
    }
    return render(request, 'guest/guest_farm_mapping_with_images.html', context)

@admin_required
@csrf_exempt
def get_farm_data_api(request):
    """API endpoint for farm CRUD operations"""
    global SAMPLE_FARMS  # ✅ Declare once at the top

    if request.method == 'GET':
        return JsonResponse({
            'success': True,
            'farms': SAMPLE_FARMS
        })

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_farm = {
                'id': len(SAMPLE_FARMS) + 1,
                'name': data.get('name'),
                'municipality': data.get('municipality'),
                'barangay': data.get('barangay'),
                'area': float(data.get('area', 0)),
                'trees': int(data.get('trees', 0)),
                'status': data.get('status', 'Active'),
                'lat': float(data.get('lat', 0)),
                'lng': float(data.get('lng', 0)),
                'description': data.get('description', ''),
                'contact': data.get('contact', ''),
                'created_at': '2024-01-20'
            }
            SAMPLE_FARMS.append(new_farm)
            return JsonResponse({'success': True, 'message': 'Farm added successfully', 'farm': new_farm})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            farm_id = data.get('id')
            for i, farm in enumerate(SAMPLE_FARMS):
                if farm['id'] == farm_id:
                    SAMPLE_FARMS[i].update(data)
                    return JsonResponse({'success': True, 'message': 'Farm updated successfully', 'farm': SAMPLE_FARMS[i]})
            return JsonResponse({'success': False, 'error': 'Farm not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            farm_id = data.get('id')
            SAMPLE_FARMS = [farm for farm in SAMPLE_FARMS if farm['id'] != farm_id]
            return JsonResponse({'success': True, 'message': 'Farm deleted successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@user_required
@csrf_exempt
def api_user_farm_request(request):
    """API endpoint for user farm registration requests"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Process farm registration request
            request_data = {
                'user_id': request.session.get('uid'),
                'user_name': request.session.get('name'),
                'farm_name': data.get('farm_name'),
                'location': data.get('location'),
                'contact': data.get('contact'),
                'description': data.get('description'),
                'status': 'pending',
                'submitted_at': '2024-01-20'
            }
            
            # In real implementation, save to database/Firebase
            
            return JsonResponse({
                'success': True,
                'message': 'Farm registration request submitted successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

def api_public_farms(request):
    """Public API endpoint for guest access to farm data"""
    if request.method == 'GET':
        # Return only public information
        public_farms = []
        for farm in SAMPLE_FARMS:
            public_farm = {
                'id': farm['id'],
                'name': farm['name'],
                'municipality': farm['municipality'],
                'barangay': farm['barangay'],
                'area': farm['area'],
                'trees': farm['trees'],
                'status': farm['status'],
                'lat': farm['lat'],
                'lng': farm['lng'],
                'description': farm['description']
            }
            public_farms.append(public_farm)
        
        return JsonResponse({
            'success': True,
            'farms': public_farms,
            'total_farms': len(public_farms),
            'total_area': sum(farm['area'] for farm in public_farms),
            'total_trees': sum(farm['trees'] for farm in public_farms)
        })

# Fixed views for the farm mapping system

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .decorators import admin_required, user_required
import json

# Sample farm data with images - replace with your database/Firebase integration
SAMPLE_FARMS = [
    {
        'id': 1,
        'name': 'Barangay Poblacion Farm',
        'municipality': 'Victoria',
        'barangay': 'Poblacion',
        'area': 4.5,
        'trees': 10,
        'status': 'Active',
        'lat': 13.1375,
        'lng': 121.2410,
        'description': 'Primary cacao growing area with established farms',
        'contact': 'Brgy. Captain Juan Santos',
        'created_at': '2024-01-15',
        'images': [
            '/static/images/download (2).jpg',
            '/static/images/download (1).jpg',
            '/static/images/download (3).jpg'
        ]

    },
    {
        'id': 2,
        'name': 'San Vicente Cacao Farm',
        'municipality': 'Victoria',
        'barangay': 'San Vicente',
        'area': 3.2,
        'trees': 15,
        'status': 'Active',
        'lat': 13.1500,
        'lng': 121.2333,
        'description': 'Emerging farming community with modern techniques',
        'contact': 'Brgy. Captain Maria Cruz',
        'created_at': '2024-01-14',
        'images': [
            '/static/images/download (1).jpg',
            '/static/images/download.jpg'
        ]
    },
    {
        'id': 3,
        'name': 'Macatoc Cacao Farm',
        'municipality': 'Victoria',
        'barangay': 'Macatoc',
        'area': 8.5,
        'trees': 13,
        'status': 'Monitoring',
        'lat': 13.1440,
        'lng': 121.2320,
        'description': 'Large scale cacao production facility',
        'contact': 'Farm Manager Pedro Reyes',
        'created_at': '2024-01-13',
        'images': [
            '/static/images/download (3).jpg',
            '/static/images/download (2).jpg'
        ]
    }
]

@admin_required
def farm_location(request):
    """Admin farm management view with CRUD and analytics"""
    context = {
        'page_title': 'Farm Management',
        'farms_data': SAMPLE_FARMS,
        'total_farms': len(SAMPLE_FARMS),
        'total_area': sum(farm['area'] for farm in SAMPLE_FARMS),
        'total_trees': sum(farm['trees'] for farm in SAMPLE_FARMS),
        'municipalities': list(set(farm['municipality'] for farm in SAMPLE_FARMS))
    }
    return render(request, 'admin/farm_location_fixed.html', context)

@user_required
def farm_mapping(request):
    """User farm mapping view with interactive features"""
    context = {
        'page_title': 'Farm Mapping',
        'description': 'Explore and interact with farm data',
        'farms_data': SAMPLE_FARMS,
        'user_name': request.session.get('name', 'User'),
        'user_role': request.session.get('role', 'User')
    }
    return render(request, 'user/farm_mapping.html', context)

def guest_farm_mapping(request):
    """Guest farm mapping view - read-only access"""
    # Filter data for public viewing (remove sensitive information)
    public_farms = []
    for farm in SAMPLE_FARMS:
        public_farm = {
            'id': farm['id'],
            'name': farm['name'],
            'municipality': farm['municipality'],
            'barangay': farm['barangay'],
            'area': farm['area'],
            'trees': farm['trees'],
            'status': farm['status'],
            'lat': farm['lat'],
            'lng': farm['lng'],
            'description': farm['description'],
            'images': farm.get('images', [])  # Include images for guest view
            # Exclude contact and other sensitive info
        }
        public_farms.append(public_farm)
    
    context = {
        'farms_data': public_farms,
        'total_farms': len(public_farms),
        'total_area': sum(farm['area'] for farm in public_farms),
        'total_trees': sum(farm['trees'] for farm in public_farms)
    }
    return render(request, 'guest/guest_farm_mapping.html', context)

@admin_required
@csrf_exempt
def api_farms_crud(request):
    """API endpoint for farm CRUD operations"""
    global SAMPLE_FARMS
    
    if request.method == 'GET':
        return JsonResponse({
            'success': True,
            'farms': SAMPLE_FARMS
        })
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Add new farm logic here
            new_farm = {
                'id': len(SAMPLE_FARMS) + 1,
                'name': data.get('name'),
                'municipality': data.get('municipality'),
                'barangay': data.get('barangay'),
                'area': float(data.get('area', 0)),
                'trees': int(data.get('trees', 0)),
                'status': data.get('status', 'Active'),
                'lat': float(data.get('lat', 0)),
                'lng': float(data.get('lng', 0)),
                'description': data.get('description', ''),
                'contact': data.get('contact', ''),
                'created_at': '2024-01-20',
                'images': data.get('images', [])
            }
            SAMPLE_FARMS.append(new_farm)
            
            return JsonResponse({
                'success': True,
                'message': 'Farm added successfully',
                'farm': new_farm
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            farm_id = data.get('id')
            
            # Update farm logic here
            for i, farm in enumerate(SAMPLE_FARMS):
                if farm['id'] == farm_id:
                    SAMPLE_FARMS[i].update(data)
                    return JsonResponse({
                        'success': True,
                        'message': 'Farm updated successfully',
                        'farm': SAMPLE_FARMS[i]
                    })
            
            return JsonResponse({
                'success': False,
                'error': 'Farm not found'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            farm_id = data.get('id')
            
            # Delete farm logic here
            SAMPLE_FARMS[:] = [farm for farm in SAMPLE_FARMS if farm['id'] != farm_id]
            
            return JsonResponse({
                'success': True,
                'message': 'Farm deleted successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

@user_required
@csrf_exempt
def api_user_farm_request(request):
    """API endpoint for user farm registration requests"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Process farm registration request
            request_data = {
                'user_id': request.session.get('uid'),
                'user_name': request.session.get('name'),
                'farm_name': data.get('farm_name'),
                'location': data.get('location'),
                'contact': data.get('contact'),
                'description': data.get('description'),
                'status': 'pending',
                'submitted_at': '2024-01-20'
            }
            
            # In real implementation, save to database/Firebase
            
            return JsonResponse({
                'success': True,
                'message': 'Farm registration request submitted successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

def api_public_farms(request):
    """Public API endpoint for guest access to farm data"""
    if request.method == 'GET':
        # Return only public information
        public_farms = []
        for farm in SAMPLE_FARMS:
            public_farm = {
                'id': farm['id'],
                'name': farm['name'],
                'municipality': farm['municipality'],
                'barangay': farm['barangay'],
                'area': farm['area'],
                'trees': farm['trees'],
                'status': farm['status'],
                'lat': farm['lat'],
                'lng': farm['lng'],
                'description': farm['description'],
                'images': farm.get('images', [])
            }
            public_farms.append(public_farm)
        
        return JsonResponse({
            'success': True,
            'farms': public_farms,
            'total_farms': len(public_farms),
            'total_area': sum(farm['area'] for farm in public_farms),
            'total_trees': sum(farm['trees'] for farm in public_farms)
        })

# Updated views with Firebase integration

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .decorators import admin_required, user_required
import json
import firebase_admin
from firebase_admin import credentials, firestore
from django.conf import settings
import os

# Firebase and Firestore already initialized in firebase_config module

@admin_required
def farm_location(request):
    """Admin farm management view with Firebase integration"""
    context = {
        'page_title': 'Farm Management',
        'description': 'Manage cacao farms with real-time updates'
    }
    return render(request, 'admin/farm_location.html', context)

@user_required
def farm_mapping(request):
    """User farm mapping view with Firebase integration"""
    context = {
        'page_title': 'Farm Mapping',
        'description': 'Explore and interact with farm data',
        'user_name': request.session.get('name', 'User'),
        'user_role': request.session.get('role', 'User')
    }
    return render(request, 'user/farm_mapping.html', context)

def guest_farm_mapping(request):
    """Guest farm mapping view with Firebase integration"""
    context = {
        'page_title': 'Farm Mapping',
        'description': 'Explore cacao farms across Oriental Mindoro'
    }
    return render(request, 'guest/guest_farm_mapping.html', context)


@csrf_exempt
def api_farms_firebase(request):
    """API endpoint for Firebase farm operations"""
    
    if request.method == 'GET':
        try:
            # Get all farms from Firebase
            farms_ref = db.collection('farms')
            docs = farms_ref.stream()
            
            farms = []
            for doc in docs:
                farm_data = doc.to_dict()
                farm_data['id'] = doc.id
                farms.append(farm_data)
            
            return JsonResponse({
                'success': True,
                'farms': farms
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Add new farm to Firebase
            farm_data = {
                'name': data.get('name'),
                'municipality': data.get('municipality'),
                'barangay': data.get('barangay'),
                'area': float(data.get('area', 0)),
                'trees': int(data.get('trees', 0)),
                'status': data.get('status', 'Active'),
                'lat': float(data.get('lat', 0)) if data.get('lat') else None,
                'lng': float(data.get('lng', 0)) if data.get('lng') else None,
                'description': data.get('description', ''),
                'images': data.get('images', []),
                'createdAt': firestore.SERVER_TIMESTAMP,
                'updatedAt': firestore.SERVER_TIMESTAMP
            }
            
            # Add to Firebase
            doc_ref = db.collection('farms').add(farm_data)
            
            return JsonResponse({
                'success': True,
                'message': 'Farm added successfully',
                'id': doc_ref[1].id
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            farm_id = data.get('id')
            
            if not farm_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Farm ID is required'
                })
            
            # Update farm in Firebase
            update_data = {
                'name': data.get('name'),
                'municipality': data.get('municipality'),
                'barangay': data.get('barangay'),
                'area': float(data.get('area', 0)),
                'trees': int(data.get('trees', 0)),
                'status': data.get('status', 'Active'),
                'lat': float(data.get('lat', 0)) if data.get('lat') else None,
                'lng': float(data.get('lng', 0)) if data.get('lng') else None,
                'description': data.get('description', ''),
                'updatedAt': firestore.SERVER_TIMESTAMP
            }
            
            # Update in Firebase
            db.collection('farms').document(farm_id).update(update_data)
            
            return JsonResponse({
                'success': True,
                'message': 'Farm updated successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            farm_id = data.get('id')
            
            if not farm_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Farm ID is required'
                })
            
            # Delete from Firebase
            db.collection('farms').document(farm_id).delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Farm deleted successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

def api_public_farms_firebase(request):
    """Public API endpoint for guest access to Firebase farm data"""
    if request.method == 'GET':
        try:
            # Get all farms from Firebase
            farms_ref = db.collection('farms')
            docs = farms_ref.stream()
            
            public_farms = []
            for doc in docs:
                farm_data = doc.to_dict()
                # Filter out sensitive information for public access
                public_farm = {
                    'id': doc.id,
                    'name': farm_data.get('name'),
                    'municipality': farm_data.get('municipality'),
                    'barangay': farm_data.get('barangay'),
                    'area': farm_data.get('area'),
                    'trees': farm_data.get('trees'),
                    'status': farm_data.get('status'),
                    'lat': farm_data.get('lat'),
                    'lng': farm_data.get('lng'),
                    'description': farm_data.get('description'),
                    'images': farm_data.get('images', [])
                }
                public_farms.append(public_farm)
            
            return JsonResponse({
                'success': True,
                'farms': public_farms,
                'total_farms': len(public_farms),
                'total_area': sum(farm.get('area', 0) for farm in public_farms),
                'total_trees': sum(farm.get('trees', 0) for farm in public_farms)
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


@csrf_exempt
def api_user_farm_request_firebase(request):
    """API endpoint for user farm registration requests with Firebase"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Process farm registration request
            request_data = {
                'user_id': request.session.get('uid'),
                'user_name': request.session.get('name'),
                'farm_name': data.get('farm_name'),
                'location': data.get('location'),
                'contact': data.get('contact'),
                'description': data.get('description'),
                'status': 'pending',
                'submitted_at': firestore.SERVER_TIMESTAMP
            }
            
            # Save to Firebase
            db.collection('farm_requests').add(request_data)
            
            return JsonResponse({
                'success': True,
                'message': 'Farm registration request submitted successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })



from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .firebase_config import auth
import requests
import time
import jwt
from functools import wraps
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .decorators import admin_required, user_required, guest_required
import json
from datetime import datetime, timedelta
import uuid
import os
import numpy as np
from PIL import Image
import firebase_admin
from firebase_admin import credentials, firestore, storage
from google.cloud.firestore_v1.base_query import FieldFilter

FIREBASE_WEB_API_KEY = 'AIzaSyAs90apE9AG6k4aIg9MpJD750OsvVD70m4'
SECRET_KEY = '49qVayZTdlh0rkFE8uxB0mh6IrdILzk8s0v1z0UZ'

# Initialize Firestore

# Sample farm data with images - this will be replaced by Firebase data
SAMPLE_FARMS = [
    {
        'id': 1,
        'name': 'Barangay Poblacion Farm',
        'municipality': 'Victoria',
        'barangay': 'Poblacion',
        'area': 4.5,
        'trees': 10,
        'status': 'Active',
        'lat': 13.1375,
        'lng': 121.2410,
        'description': 'Primary cacao growing area with established farms',
        'contact': 'Brgy. Captain Juan Santos',
        'created_at': '2024-01-15',
        'images': [
            '/static/images/download (2).jpg',
            '/static/images/download (1).jpg',
            '/static/images/download (3).jpg'
        ]

    },
    {
        'id': 2,
        'name': 'San Vicente Cacao Farm',
        'municipality': 'Victoria',
        'barangay': 'San Vicente',
        'area': 3.2,
        'trees': 15,
        'status': 'Active',
        'lat': 13.1500,
        'lng': 121.2333,
        'description': 'Emerging farming community with modern techniques',
        'contact': 'Brgy. Captain Maria Cruz',
        'created_at': '2024-01-14',
        'images': [
            '/static/images/download (1).jpg',
            '/static/images/download.jpg'
        ]
    },
    {
        'id': 3,
        'name': 'Macatoc Cacao Farm',
        'municipality': 'Victoria',
        'barangay': 'Macatoc',
        'area': 8.5,
        'trees': 13,
        'status': 'Monitoring',
        'lat': 13.1440,
        'lng': 121.2320,
        'description': 'Large scale cacao production facility',
        'contact': 'Farm Manager Pedro Reyes',
        'created_at': '2024-01-13',
        'images': [
            '/static/images/download (3).jpg',
            '/static/images/download (2).jpg'
        ]
    }
]

# Global list to store pending farm requests
PENDING_FARM_REQUESTS = []



@admin_required
def admin_dashboard(request):
    print("[DEBUG] Accessing Admin Dashboard:", request.session.get('user_email'), request.session.get('role'))
    
    # Get farm statistics
    try:
        farms_ref = db.collection('farms')
        farms_docs = list(farms_ref.stream())
        
        # Combine Firebase farms with sample farms and pending requests
        farms_data = SAMPLE_FARMS.copy()
        
        # Add Firebase farms
        for doc in farms_docs:
            farm_data = doc.to_dict()
            farm_data['id'] = doc.id
            farms_data.append(farm_data)
        
        # Add pending farm requests as "Pending" status farms
        for request_data in PENDING_FARM_REQUESTS:
            pending_farm = {
                'id': f"pending_{request_data['id']}",
                'name': request_data['farm_name'],
                'municipality': request_data.get('municipality', 'Unknown'),
                'barangay': request_data.get('barangay', 'Unknown'),
                'area': request_data.get('area', 0),
                'trees': request_data.get('trees', 0),
                'status': 'Pending Approval',
                'lat': request_data.get('lat'),
                'lng': request_data.get('lng'),
                'description': request_data.get('description', ''),
                'contact': request_data.get('contact', ''),
                'created_at': request_data.get('submitted_at', ''),
                'user_name': request_data.get('user_name', ''),
                'user_id': request_data.get('user_id', ''),
                'images': ['/static/images/download.jpg'],
                'is_pending': True
            }
            farms_data.append(pending_farm)
        
        total_farms = len(farms_data)
        total_area = sum(farm.get('area', 0) for farm in farms_data)
        total_trees = sum(farm.get('trees', 0) for farm in farms_data)
        active_farms = len([f for f in farms_data if f.get('status') == 'Active'])
        pending_farms = len([f for f in farms_data if f.get('status') == 'Pending Approval'])
        
    except Exception as e:
        print(f"Error fetching farm data: {e}")
        farms_data = SAMPLE_FARMS.copy()
        total_farms = len(farms_data)
        total_area = sum(farm.get('area', 0) for farm in farms_data)
        total_trees = sum(farm.get('trees', 0) for farm in farms_data)
        active_farms = len([f for f in farms_data if f.get('status') == 'Active'])
        pending_farms = 0

    context = {
        'name': request.session.get('name'),
        'email': request.session.get('user_email'),
        'role': request.session.get('role'),
        'total_farms': total_farms,
        'total_area': total_area,
        'total_trees': total_trees,
        'active_farms': active_farms,
        'pending_farms': pending_farms,
    }
    return render(request, 'admin/admin_dashboard.html', context)

@user_required
def userdashboard(request):
    print("[DEBUG] Accessing User Dashboard:", request.session.get('user_email'), request.session.get('role'))

    if request.session.get('role') == 'guest':
        messages.error(request, "Guest users cannot access user dashboard.")
        return redirect('guest_dashboard')

    context = {
        'name': request.session.get('name'),
        'email': request.session.get('user_email'),
        'role': request.session.get('role'),
        'uid': request.session.get('uid')
    }
    return render(request, 'user/userdashboard.html', context)

def guest_dashboard(request):
    context = {
        'total_farms': len(SAMPLE_FARMS),
        'total_area': sum(farm.get('area', 0) for farm in SAMPLE_FARMS),
        'total_trees': sum(farm.get('trees', 0) for farm in SAMPLE_FARMS)
    }
    return render(request, 'guest/guest_dashboard.html', context)

# Farm Mapping Views
@admin_required
def farm_location(request):
    """Admin farm management view with CRUD and analytics"""
    context = {
        'page_title': 'Farm Management',
        'farms_data': SAMPLE_FARMS,
        'total_farms': len(SAMPLE_FARMS),
        'total_area': sum(farm['area'] for farm in SAMPLE_FARMS),
        'total_trees': sum(farm['trees'] for farm in SAMPLE_FARMS),
        'municipalities': list(set(farm['municipality'] for farm in SAMPLE_FARMS))
    }
    return render(request, 'admin/farm_location.html', context)

@user_required
def farm_mapping(request):
    """User farm mapping view with interactive features"""
    context = {
        'page_title': 'Farm Mapping',
        'description': 'Explore and interact with farm data',
        'farms_data': SAMPLE_FARMS,
        'user_name': request.session.get('name', 'User'),
        'user_role': request.session.get('role', 'User')
    }
    return render(request, 'user/farm_mapping.html', context)

def guest_farm_mapping(request):
    """Guest farm mapping view - read-only access"""
    # Filter data for public viewing (remove sensitive information)
    public_farms = []
    for farm in SAMPLE_FARMS:
        public_farm = {
            'id': farm['id'],
            'name': farm['name'],
            'municipality': farm['municipality'],
            'barangay': farm['barangay'],
            'area': farm['area'],
            'trees': farm['trees'],
            'status': farm['status'],
            'lat': farm['lat'],
            'lng': farm['lng'],
            'description': farm['description'],
            'images': farm.get('images', [])
        }
        public_farms.append(public_farm)
    
    context = {
        'farms_data': public_farms,
        'total_farms': len(public_farms),
        'total_area': sum(farm['area'] for farm in public_farms),
        'total_trees': sum(farm['trees'] for farm in public_farms)
    }
    return render(request, 'guest/guest_farm_mapping.html', context)

# API Endpoints for Farm Operations
@csrf_exempt
def api_farms_firebase(request):
    """API endpoint for Firebase farm operations"""
    global SAMPLE_FARMS, PENDING_FARM_REQUESTS
    
    if request.method == 'GET':
        try:
            # Try to get farms from Firebase first
            farms_ref = db.collection('farms')
            docs = farms_ref.stream()
            
            farms = []
            for doc in docs:
                farm_data = doc.to_dict()
                farm_data['id'] = doc.id
                farms.append(farm_data)
            
            # Combine with sample farms
            all_farms = SAMPLE_FARMS.copy()
            all_farms.extend(farms)
            
            # Add pending farm requests
            for request_data in PENDING_FARM_REQUESTS:
                pending_farm = {
                    'id': f"pending_{request_data['id']}",
                    'name': request_data['farm_name'],
                    'municipality': request_data.get('municipality', 'Unknown'),
                    'barangay': request_data.get('barangay', 'Unknown'),
                    'area': request_data.get('area', 0),
                    'trees': request_data.get('trees', 0),
                    'status': 'Pending Approval',
                    'lat': request_data.get('lat'),
                    'lng': request_data.get('lng'),
                    'description': request_data.get('description', ''),
                    'contact': request_data.get('contact', ''),
                    'created_at': request_data.get('submitted_at', ''),
                    'user_name': request_data.get('user_name', ''),
                    'user_id': request_data.get('user_id', ''),
                    'images': ['/static/images/download.jpg'],
                    'is_pending': True
                }
                all_farms.append(pending_farm)
            
            return JsonResponse({
                'success': True,
                'farms': all_farms
            })
        except Exception as e:
            # Fallback to sample data if Firebase fails
            return JsonResponse({
                'success': True,
                'farms': SAMPLE_FARMS.copy()
            })
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Add new farm
            farm_data = {
                'name': data.get('name'),
                'municipality': data.get('municipality'),
                'barangay': data.get('barangay'),
                'area': float(data.get('area', 0)),
                'trees': int(data.get('trees', 0)),
                'status': data.get('status', 'Active'),
                'lat': float(data.get('lat', 0)) if data.get('lat') else None,
                'lng': float(data.get('lng', 0)) if data.get('lng') else None,
                'description': data.get('description', ''),
                'contact': data.get('contact', ''),
                'images': ['/static/images/download.jpg', '/static/images/download (1).jpg'],
                'created_at': datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d')
            }
            
            try:
                # Try to add to Firebase
                doc_ref = db.collection('farms').add(farm_data)
                farm_data['id'] = doc_ref[1].id
            except Exception as firebase_error:
                # If Firebase fails, add to sample data
                print(f"Firebase error: {firebase_error}")
                farm_data['id'] = max([f['id'] for f in SAMPLE_FARMS]) + 1 if SAMPLE_FARMS else 1
                SAMPLE_FARMS.append(farm_data)
            
            return JsonResponse({
                'success': True,
                'message': 'Farm added successfully',
                'farm': farm_data
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            farm_id = data.get('id')
            
            if not farm_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Farm ID is required'
                })
            
            # Update farm data
            update_data = {
                'name': data.get('name'),
                'municipality': data.get('municipality'),
                'barangay': data.get('barangay'),
                'area': float(data.get('area', 0)),
                'trees': int(data.get('trees', 0)),
                'status': data.get('status', 'Active'),
                'lat': float(data.get('lat', 0)) if data.get('lat') else None,
                'lng': float(data.get('lng', 0)) if data.get('lng') else None,
                'description': data.get('description', ''),
                'contact': data.get('contact', ''),
            }
            
            try:
                # Try to update in Firebase
                db.collection('farms').document(str(farm_id)).update(update_data)
            except Exception as firebase_error:
                # If Firebase fails, update sample data
                print(f"Firebase error: {firebase_error}")
                for i, farm in enumerate(SAMPLE_FARMS):
                    if str(farm['id']) == str(farm_id):
                        SAMPLE_FARMS[i].update(update_data)
                        break
            
            return JsonResponse({
                'success': True,
                'message': 'Farm updated successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            farm_id = data.get('id')
            
            if not farm_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Farm ID is required'
                })
            
            # Check if it's a pending request
            if str(farm_id).startswith('pending_'):
                request_id = int(str(farm_id).replace('pending_', ''))
                PENDING_FARM_REQUESTS[:] = [req for req in PENDING_FARM_REQUESTS if req['id'] != request_id]
                return JsonResponse({
                    'success': True,
                    'message': 'Pending farm request deleted successfully'
                })
            
            try:
                # Try to delete from Firebase
                db.collection('farms').document(str(farm_id)).delete()
            except Exception as firebase_error:
                # If Firebase fails, delete from sample data
                print(f"Firebase error: {firebase_error}")
            
            # Remove from sample data
            SAMPLE_FARMS[:] = [farm for farm in SAMPLE_FARMS if str(farm['id']) != str(farm_id)]
        
            return JsonResponse({
                'success': True,
                'message': 'Farm deleted successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

@csrf_exempt
def api_public_farms_firebase(request):
    """Public API endpoint for guest access to Firebase farm data"""
    if request.method == 'GET':
        try:
            # Try to get farms from Firebase first
            farms_ref = db.collection('farms')
            docs = farms_ref.stream()
            
            public_farms = []
            for doc in docs:
                farm_data = doc.to_dict()
                # Filter out sensitive information for public access
                public_farm = {
                    'id': doc.id,
                    'name': farm_data.get('name'),
                    'municipality': farm_data.get('municipality'),
                    'barangay': farm_data.get('barangay'),
                    'area': farm_data.get('area'),
                    'trees': farm_data.get('trees'),
                    'status': farm_data.get('status'),
                    'lat': farm_data.get('lat'),
                    'lng': farm_data.get('lng'),
                    'description': farm_data.get('description'),
                    'images': farm_data.get('images', [])
                }
                public_farms.append(public_farm)
            
            # Add sample farms (only approved ones for public)
            for farm in SAMPLE_FARMS:
                if farm.get('status') != 'Pending Approval':
                    public_farm = {
                        'id': farm['id'],
                        'name': farm['name'],
                        'municipality': farm['municipality'],
                        'barangay': farm['barangay'],
                        'area': farm['area'],
                        'trees': farm['trees'],
                        'status': farm['status'],
                        'lat': farm['lat'],
                        'lng': farm['lng'],
                        'description': farm['description'],
                        'images': farm.get('images', [])
                    }
                    public_farms.append(public_farm)
            
            return JsonResponse({
                'success': True,
                'farms': public_farms,
                'total_farms': len(public_farms),
                'total_area': sum(farm.get('area', 0) for farm in public_farms),
                'total_trees': sum(farm.get('trees', 0) for farm in public_farms)
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

@csrf_exempt
def api_user_farm_request_firebase(request):
    """API endpoint for user farm registration requests with Firebase"""
    global PENDING_FARM_REQUESTS
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Generate unique ID for the request
            request_id = len(PENDING_FARM_REQUESTS) + 1
            
            # Parse location to extract municipality and barangay
            location = data.get('location', '')
            location_parts = location.split(',')
            municipality = location_parts[0].strip() if len(location_parts) > 0 else 'Unknown'
            barangay = location_parts[1].strip() if len(location_parts) > 1 else 'Unknown'
            
            # Process farm registration request
            request_data = {
                'id': request_id,
                'user_id': request.session.get('uid'),
                'user_name': request.session.get('name'),
                'farm_name': data.get('farm_name'),
                'location': location,
                'municipality': municipality,
                'barangay': barangay,
                'contact': data.get('contact'),
                'description': data.get('description'),
                'area': float(data.get('area', 0)) if data.get('area') else 0,
                'trees': int(data.get('trees', 0)) if data.get('trees') else 0,
                'status': 'pending',
                'submitted_at': datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S'),
                'lat': None,  # Will be set by admin
                'lng': None   # Will be set by admin
            }
            
            # Add to pending requests
            PENDING_FARM_REQUESTS.append(request_data)
            
            try:
                # Also save to Firebase
                db.collection('farm_requests').add(request_data)
            except Exception as firebase_error:
                print(f"Firebase error: {firebase_error}")
                # Continue even if Firebase fails, we have local storage
            
            return JsonResponse({
                'success': True,
                'message': 'Farm registration request submitted successfully! It will be reviewed by administrators.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

@csrf_exempt
def api_approve_farm_request(request):
    """API endpoint for admins to approve pending farm requests"""
    global PENDING_FARM_REQUESTS, SAMPLE_FARMS
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            request_id = data.get('request_id')
            
            if not request_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Request ID is required'
                })
            
            # Find the pending request
            pending_request = None
            for req in PENDING_FARM_REQUESTS:
                if req['id'] == int(request_id):
                    pending_request = req
                    break
            
            if not pending_request:
                return JsonResponse({
                    'success': False,
                    'error': 'Pending request not found'
                })
            
            # Create approved farm
            approved_farm = {
                'id': max([f['id'] for f in SAMPLE_FARMS]) + 1 if SAMPLE_FARMS else 1,
                'name': pending_request['farm_name'],
                'municipality': pending_request['municipality'],
                'barangay': pending_request['barangay'],
                'area': pending_request['area'],
                'trees': pending_request['trees'],
                'status': 'Active',
                'lat': data.get('lat', 13.1400),  # Default coordinates if not provided
                'lng': data.get('lng', 121.2400),
                'description': pending_request['description'],
                'contact': pending_request['contact'],
                'created_at': datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d'),
                'images': ['/static/images/download.jpg', '/static/images/download (1).jpg']
            }
            
            # Add to approved farms
            SAMPLE_FARMS.append(approved_farm)
            
            # Remove from pending requests
            PENDING_FARM_REQUESTS[:] = [req for req in PENDING_FARM_REQUESTS if req['id'] != int(request_id)]
            
            # Update the request status in Firebase
            try:
                # Find and update the farm request in Firebase
                farm_requests_ref = db.collection('farm_requests')
                query = farm_requests_ref.where('id', '==', int(request_id))
                docs = list(query.stream())
                
                for doc in docs:
                    doc.reference.update({
                        'status': 'approved',
                        'approved_at': datetime.now(pytz.timezone('Asia/Manila')),
                        'approved_by': request.session.get('user_email', 'admin')
                    })
            except Exception as firebase_error:
                print(f"Firebase update error: {firebase_error}")
            
            try:
                # Also save to Firebase
                db.collection('farms').add(approved_farm)
            except Exception as firebase_error:
                print(f"Firebase error: {firebase_error}")
            
            return JsonResponse({
                'success': True,
                'message': 'Farm request approved successfully!',
                'farm': approved_farm
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

def terms_view(request):
    return render(request, 'accounts/terms.html')

def privacy_view(request):
    return render(request, 'accounts/privacy.html')

# --------------------------------------------
# Scan and Diagnose
# --------------------------------------------

# Django core imports
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

# Utilities and system
import os
import json
import time
import uuid
import jwt
import requests
import numpy as np
from PIL import Image
from datetime import datetime, timedelta
from functools import wraps
from random import choice, uniform

# Firebase and Firestore
import firebase_admin
from firebase_admin import credentials, firestore, storage
from .firebase_config import auth
from google.cloud.firestore_v1.base_query import FieldFilter

# Custom decorators
from .decorators import admin_required, user_required

# Firebase keys
FIREBASE_WEB_API_KEY = 'AIzaSyAs90apE9AG6k4aIg9MpJD750OsvVD70m4'
SECRET_KEY = '49qVayZTdlh0rkFE8uxB0mh6IrdILzk8s0v1z0UZ'

# Initialize Firestore client

# --------------------------------------------
# Disease Classes and Recommendations
# --------------------------------------------
DISEASE_CLASSES = [
    'Black Pod Rot',
    'Fito Disease',
    'Healthy',
    'Monilia Disease',
    'Unknown',
    'Mirids'
]

PEST_CLASSES = [
    'Ant Weaver',
    'Aphids',
    'Healthy',
    'Mealy Bug',
    'Unknown Data',
    'Cocoa Pod Borer'
]

# Disease Recommendations
DISEASE_RECOMMENDATIONS = {
    'Black Pod Rot': [
        'Remove and destroy infected pods immediately',
        'Improve drainage and air circulation',
        'Apply copper-based fungicides',
        'Harvest ripe pods promptly'
    ],
    'Fito Disease': [
        'Improve soil drainage and reduce waterlogging',
        'Remove and destroy infected plant parts',
        'Apply recommended fungicides as preventive measure',
        'Monitor plants regularly for new symptoms'
    ],
    'Healthy': [
        'Continue current management practices',
        'Regular monitoring for early detection',
        'Maintain proper nutrition and irrigation',
        'Keep farm clean and well-maintained'
    ],
    'Monilia Disease': [
        'Remove infected pods and plant debris',
        'Prune to improve air circulation',
        'Apply protective fungicides during wet season',
        'Plant resistant varieties when available'
    ],
    'Unknown': [
        'Monitor affected plants closely for symptom progression',
        'Consult local agricultural expert for accurate diagnosis',
        'Avoid unnecessary chemical applications',
        'Document and report unusual symptoms for research'
    ],
    'Mirids': [
        'Prune and destroy infested shoots',
        'Apply recommended insecticide if population is high',
        'Encourage natural predators like wasps and ants',
        'Regular monitoring and early intervention'
    ]
}

PEST_RECOMMENDATIONS = {
    'Ant Weaver': [
        'Locate and destroy ant nests around plantation',
        'Trim branches touching each other to prevent ant movement',
        'Use baiting techniques with approved insecticides',
        'Encourage natural predators of ants'
    ],
    'Aphids': [
        'Encourage natural predators like lady beetles',
        'Use reflective mulches to repel aphids',
        'Apply insecticidal soap or neem oil',
        'Remove heavily infested shoots'
    ],
    'Healthy': [
        'Continue integrated pest management',
        'Regular monitoring for early detection',
        'Maintain beneficial insect populations',
        'Keep plantation clean and well-managed'
    ],
    'Mealy Bug': [
        'Introduce natural enemies such as parasitoids',
        'Apply systemic insecticides only if severe',
        'Maintain ant control to reduce mealybug spread',
        'Regularly monitor and intervene early'
    ],
    'Unknown Data': [
        'Collect samples for proper identification',
        'Avoid immediate pesticide application until confirmed',
        'Monitor population levels over several days',
        'Seek expert assistance if pest persists'
    ],
    'Cocoa Pod Borer': [
        'Harvest pods every 7-10 days to break pest cycle',
        'Remove and destroy infested pods immediately',
        'Install pheromone traps to monitor population',
        'Apply biological control agents such as Trichogramma'
    ]
}


# ----------------------------
# User Scan Diagnose View
# ----------------------------
def scan_diagnose(request):
    """User scan diagnose view"""
    context = {
        'uid': request.session.get('uid'),
        'user_email': request.session.get('user_email'),
        'role': request.session.get('role', 'user')
    }
    return render(request, 'user/scan_diagnose.html', context)

# ----------------------------
# Guest Scan Diagnose View
# ----------------------------
def guest_scan_diagnose(request):
    """Guest scan diagnose view"""
    today = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d')
    session_key = f'guest_limits_{today}'

    if session_key not in request.session:
        request.session[session_key] = {'disease': 0, 'pest': 0}

    context = {
        'daily_limits': request.session[session_key],
        'max_daily_scans': 5,
        'today': today
    }
    return render(request, 'guest/guest_scan_diagnose.html', context)

# ----------------------------
# Simulated ML Analysis
# ----------------------------
from random import choice, uniform


# ----------------------------
# Scan Image Handler
# ----------------------------
@csrf_exempt
def scan_image(request):
    """Handle image scanning for both users and guests"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

    try:
        scan_type = request.POST.get('scan_type', 'disease')
        image_file = request.FILES.get('image')
        if not image_file:
            return JsonResponse({'success': False, 'message': 'No image provided'})

        # Default guest
        user_type, user_id, user_email = 'guest', 'guest', 'guest@example.com'

        if request.session.get('uid'):
            user_type = 'user'
            user_id = request.session.get('uid')
            user_email = request.session.get('user_email', '')
        else:
            today = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d')
            session_key = f'guest_limits_{today}'
            if session_key not in request.session:
                request.session[session_key] = {'disease': 0, 'pest': 0}
            daily_limits = request.session[session_key]
            if daily_limits.get(scan_type, 0) >= 5:
                return JsonResponse({
                    'success': False,
                    'message': f'Daily {scan_type} scan limit reached (5/5). Please sign up for unlimited scans.'
                })

        # Simulate scan
        analysis_result = simulate_analysis(scan_type, image_file)
        scan_id = str(uuid.uuid4())

        scan_data = {
            'scan_id': scan_id,
            'user_id': user_id,
            'user_email': user_email,
            'user_type': user_type,
            'type': scan_type,
            'result': analysis_result['class'],
            'confidence': analysis_result['confidence'],
            'recommendations': analysis_result['recommendations'],
            'image_name': image_file.name,
            'timestamp': firestore.SERVER_TIMESTAMP
        }

        db.collection('scans').document(scan_id).set(scan_data)

        if user_type == 'guest':
            request.session[session_key][scan_type] += 1
            request.session.modified = True

        return JsonResponse({
            'success': True,
            'scan_id': scan_id,
            'type': scan_type,
            'result': analysis_result['class'],
            'confidence': round(analysis_result['confidence'] * 100, 2),
            'recommendations': analysis_result['recommendations'],
            'remaining_scans': {
                'disease': max(0, 5 - request.session[session_key].get('disease', 0)) if user_type == 'guest' else 'unlimited',
                'pest': max(0, 5 - request.session[session_key].get('pest', 0)) if user_type == 'guest' else 'unlimited',
            }
        })
    except Exception as e:
        print(f"Error in scan_image: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Error processing scan: {str(e)}'})

# ----------------------------
# Get Scan History
# ----------------------------
def get_scan_history(request):
    """Get scan history for current user/guest"""
    try:
        if not request.session.get('uid'):
            return JsonResponse({'success': True, 'scans': []})

        user_id = request.session.get('uid')
        scans_ref = db.collection('scans').where('user_id', '==', user_id).order_by('timestamp', direction=firestore.Query.DESCENDING)
        scans = []

        for doc in scans_ref.stream():
            data = doc.to_dict()
            data['id'] = doc.id
            if 'timestamp' in data and data['timestamp']:
                data['timestamp'] = data['timestamp'].isoformat()
            scans.append(data)

        return JsonResponse({'success': True, 'scans': scans})
    except Exception as e:
        print(f"Error getting scan history: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)})

# ----------------------------
# Delete Scan (User)
# ----------------------------
@csrf_exempt
def delete_scan(request):
    """Delete a scan (user only)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

    try:
        data = json.loads(request.body)
        scan_id = data.get('scan_id')
        user_id = request.session.get('uid')
        if not user_id:
            return JsonResponse({'success': False, 'message': 'Authentication required'})
        if not scan_id:
            return JsonResponse({'success': False, 'message': 'Scan ID required'})

        scan_ref = db.collection('scans').document(scan_id)
        doc = scan_ref.get()
        if not doc.exists:
            return JsonResponse({'success': False, 'message': 'Scan not found'})
        if doc.to_dict().get('user_id') != user_id:
            return JsonResponse({'success': False, 'message': 'Unauthorized'})

        scan_ref.delete()
        return JsonResponse({'success': True, 'message': 'Scan deleted successfully'})
    except Exception as e:
        print(f"Error deleting scan: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)})

# ----------------------------
# Admin Image Analysis View
# ----------------------------
@admin_required
def image_analysis(request):
    """Admin image analysis view"""
    try:
        scan_type = request.GET.get('type', 'all')
        user_type = request.GET.get('user_type', 'all')
        confidence_level = request.GET.get('confidence', 'all')
        date_filter = request.GET.get('date', '')

        query = db.collection('scans')
        if scan_type != 'all':
            query = query.where('type', '==', scan_type)
        if user_type != 'all':
            query = query.where('user_type', '==', user_type)
        query = query.order_by('timestamp', direction=firestore.Query.DESCENDING)

        scans_data = []
        for doc in query.stream():
            data = doc.to_dict()
            data['id'] = doc.id

            if confidence_level != 'all':
                confidence = data.get('confidence', 0)
                if confidence_level == 'high' and confidence < 0.8:
                    continue
                elif confidence_level == 'medium' and (confidence < 0.6 or confidence >= 0.8):
                    continue
                elif confidence_level == 'low' and confidence >= 0.6:
                    continue

            if date_filter:
                try:
                    filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                    scan_date = data.get('timestamp')
                    if scan_date and scan_date.date() != filter_date:
                        continue
                except:
                    pass

            if 'confidence' in data:
                data['primary_confidence'] = data['confidence'] * 100

            data['username'] = data.get('user_email', 'Guest') if data.get('user_type') == 'user' else 'Guest'
            scans_data.append(data)

        context = {
            'scans': scans_data,
            'total_scans': len(scans_data),
            'filters': {
                'type': scan_type,
                'user_type': user_type,
                'confidence': confidence_level,
                'date': date_filter
            }
        }
        return render(request, 'admin/image_analysis.html', context)

    except Exception as e:
        print(f"Error in image_analysis view: {str(e)}")
        messages.error(request, f"Error loading scan data: {str(e)}")
        return render(request, 'admin/image_analysis.html', {'scans': [], 'total_scans': 0})

# ----------------------------
# Admin Delete Scan
# ----------------------------
@admin_required
@csrf_exempt
def admin_delete_scan(request, scan_id):
    """Admin delete scan"""
    if request.method == 'POST':
        try:
            ref = db.collection('scans').document(scan_id)
            doc = ref.get()
            if not doc.exists:
                messages.error(request, 'Scan not found.')
            else:
                ref.delete()
                messages.success(request, 'Scan deleted successfully.')
        except Exception as e:
            print(f"Error deleting scan: {str(e)}")
            messages.error(request, f"Error deleting scan: {str(e)}")
    return redirect('image_analysis')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import json

from .models import CustomUser, UserProfile, UserLoginLog

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def custom_login(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        return redirect('userdashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Log the login
            UserLoginLog.objects.create(
                user=user,
                ip_address=get_client_ip(request)
            )
            
            if user.role == 'admin':
                return redirect('admin_dashboard')
            return redirect('userdashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'registration/login.html')


def user_dashboard(request):
    return render(request, 'user/userdashboard.html')


def account_settings(request):
    # Get or create profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Handle form submission
        name = request.POST.get('name', '')
        phone = request.POST.get('phone', '')
        bio = request.POST.get('bio', '')
        profile_image = request.FILES.get('profile_image')
        
        # Update user name
        if name:
            name_parts = name.split(' ', 1)
            request.user.first_name = name_parts[0]
            request.user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            request.user.save()
        
        # Update profile
        profile.phone = phone
        profile.bio = bio
        if profile_image:
            profile.photo = profile_image
        profile.save()
        
        # Return JSON response for AJAX
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Profile updated successfully!'
            })
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('account_settings')
    
    return render(request, 'user/accounts.html', {'profile': profile})

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


def admin_dashboard(request):
    return render(request, 'admin/admin_dashboard.html')







from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .decorators import admin_required, user_required, guest_required
import json
from datetime import datetime, timedelta
import uuid
import os
import numpy as np
from PIL import Image
import firebase_admin
from firebase_admin import credentials, firestore, storage
from google.cloud.firestore_v1.base_query import FieldFilter
from django.utils import timezone
from django.core.paginator import Paginator
import requests

# Initialize Firestore (with error handling)
try:
    db = firestore.client()
except Exception as e:
    print(f"Firebase initialization error: {e}")
    db = None

# Sample products data for fallback
SAMPLE_PRODUCTS = [
    {
        'id': '1',
        'name': 'Premium Cacao Beans',
        'description': 'High-quality dried cacao beans from Victoria, Oriental Mindoro',
        'price': 250.00,
        'stock_quantity': 50,
        'category': 'Raw Materials',
        'product_type': 'dried_beans',
        'images': ['/static/images/cacao-beans.jpg', '/static/images/cacao-product-1.jpg'],
        'is_active': True,
        'featured': True,
        'origin': 'Victoria, Oriental Mindoro',
        'unit': 'kg'
    },
    {
        'id': '2',
        'name': 'Fresh Cacao Pods',
        'description': 'Fresh cacao pods harvested daily from local farms',
        'price': 150.00,
        'stock_quantity': 30,
        'category': 'Fresh Produce',
        'product_type': 'fresh_cacao',
        'images': ['/static/images/cacao-pods.jpg', '/static/images/fresh-cacao.jpg'],
        'is_active': True,
        'featured': False,
        'origin': 'Victoria, Oriental Mindoro',
        'unit': 'piece'
    },
    {
        'id': '3',
        'name': 'Cacao Powder',
        'description': 'Pure cacao powder perfect for baking and beverages',
        'price': 180.00,
        'stock_quantity': 25,
        'category': 'Processed',
        'product_type': 'cacao_powder',
        'images': ['/static/images/cacao-powder.jpg', '/static/images/powder-product.jpg'],
        'is_active': True,
        'featured': True,
        'origin': 'Victoria, Oriental Mindoro',
        'unit': 'pack'
    },
    {
        'id': '4',
        'name': 'Organic Cacao Nibs',
        'description': 'Roasted cacao nibs with rich chocolate flavor',
        'price': 320.00,
        'stock_quantity': 15,
        'category': 'Processed',
        'product_type': 'cacao_nibs',
        'images': ['/static/images/cacao-nibs.jpg', '/static/images/nibs-organic.jpg'],
        'is_active': True,
        'featured': True,
        'origin': 'Victoria, Oriental Mindoro',
        'unit': 'pack'
    },
    {
        'id': '5',
        'name': 'Cacao Butter',
        'description': 'Pure cacao butter for cosmetics and cooking',
        'price': 450.00,
        'stock_quantity': 20,
        'category': 'Processed',
        'product_type': 'cacao_butter',
        'images': ['/static/images/cacao-butter.jpg', '/static/images/butter-pure.jpg'],
        'is_active': True,
        'featured': False,
        'origin': 'Victoria, Oriental Mindoro',
        'unit': 'jar'
    },
    {
        'id': '6',
        'name': 'Dark Chocolate Bars',
        'description': 'Artisanal dark chocolate made from local cacao',
        'price': 120.00,
        'stock_quantity': 40,
        'category': 'Finished Products',
        'product_type': 'chocolate',
        'images': ['/static/images/dark-chocolate.jpg', '/static/images/chocolate-bar.jpg'],
        'is_active': True,
        'featured': True,
        'origin': 'Victoria, Oriental Mindoro',
        'unit': 'bar'
    }
]

#Guest_Dashboard
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone

from django.core.files.storage import default_storage
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import os
import numpy as np
import logging
import traceback
import uuid
from PIL import Image
import random
from django.utils import timezone as django_timezone
from datetime import timezone as datetime_timezone

# For current time
now = django_timezone.now()

# Set up logging
logger = logging.getLogger(__name__)

class CacaoResNet(nn.Module):
    def __init__(self, num_classes):
        super(CacaoResNet, self).__init__()
        self.resnet = resnet18(pretrained=True)
        num_ftrs = self.resnet.fc.in_features
        self.resnet.fc = nn.Linear(num_ftrs, num_classes)

    def forward(self, x):
        return self.resnet(x)

# Global variables for models
# Disease model → 5 classes
disease_model = load_pytorch_model(
    "models/cacao_disease_resnet_state_dict.pth", 
    CacaoResNet, 
    num_classes=5
)

# Pest model → 5 classes
pest_model = load_pytorch_model(
    "models/cacao_pest_resnet_state_dict.pth", 
    CacaoResNet, 
    num_classes=5
)


def load_models():
    """Load models once when needed"""
    global disease_model, pest_model
    
    try:
        if disease_model is None:
            disease_model_path = os.path.join(settings.BASE_DIR, 'models', 'cacao_disease_resnet_state_dict.pth')
            if os.path.exists(disease_model_path):
                try:
                    disease_model = CacaoResNet(num_classes=7)  # Adjust based on your classes
                    disease_model.load_state_dict(torch.load(disease_model_path, map_location='cpu'))
                    disease_model.eval()
                    logger.info("Disease model loaded successfully")
                except Exception as e:
                    logger.error(f"Error loading disease model: {e}")
                    disease_model = None
            else:
                logger.warning(f"Disease model not found at: {disease_model_path}")
        
        if pest_model is None:
            # Fix: Using correct pest model path
            pest_model_path = os.path.join(settings.BASE_DIR, 'models', 'cacao_pest_resnet_state_dict.pth')
            if os.path.exists(pest_model_path):
                try:
                    pest_model = CacaoResNet(num_classes=6)  # Adjust based on your classes
                    pest_model.load_state_dict(torch.load(pest_model_path, map_location='cpu'))
                    pest_model.eval()
                    logger.info("Pest model loaded successfully")
                except Exception as e:
                    logger.error(f"Error loading pest model: {e}")
                    pest_model = None
            else:
                logger.warning(f"Pest model not found at: {pest_model_path}")
                
    except Exception as e:
        logger.error(f"Error in load_models: {e}")

# ===============================
# RECOMMENDATIONS
# ===============================
DISEASE_RECOMMENDATIONS = {
    'Black Pod Rot': [
        'Remove infected pods immediately',
        'Improve drainage to reduce humidity',
        'Apply copper-based fungicides',
        'Prune trees to improve air circulation',
        'Harvest ripe pods quickly'
    ],
    'Fito Disease': [
        'Improve soil drainage and reduce excess moisture',
        'Apply recommended fungicides',
        'Use resistant cacao varieties if available',
        'Remove and destroy infected debris regularly',
        'Maintain proper farm sanitation'
    ],
    'Healthy': [
        'Continue current management practices',
        'Regular monitoring for early detection',
        'Maintain proper nutrition and watering',
        'Keep good farm hygiene',
        'Preventive fungicide applications during rainy season'
    ],
    'Monilia Disease': [
        'Remove infected pods and debris',
        'Apply fungicide sprays during wet season',
        'Improve farm sanitation',
        'Harvest pods regularly to minimize spread',
        'Monitor farm frequently for new infections'
    ],
    'Unknown': [
        'Unable to classify — not cacao-related or unclear',
        'Verify if the image is of cacao tree or pod',
        'Consult expert for confirmation',
        'Try uploading a clearer image'
    ],
    'Mirids': [
        'Prune infested shoots',
        'Apply recommended insecticide',
        'Encourage natural predators',
        'Regular monitoring and scouting'
    ]
}

PEST_RECOMMENDATIONS = {
    'Ant Weaver': [
        'Identify and remove ant nests if infestation is severe',
        'Prune branches to limit ant movement',
        'Encourage natural predators',
        'Monitor regularly and apply safe bait if needed',
        'Maintain clean plantation to discourage nesting'
    ],
    'Aphids': [
        'Use insecticidal soap or neem oil',
        'Introduce beneficial insects like ladybugs',
        'Remove infested shoots and leaves',
        'Control ant populations',
        'Maintain proper plant nutrition'
    ],
    'Healthy': [
        'Continue current pest management practices',
        'Regular monitoring for early detection',
        'Maintain beneficial insect populations',
        'Keep farm clean and weed-free',
        'Preventive treatments during pest season'
    ],
    'Mealy Bug': [
        'Apply systemic insecticides if severe',
        'Use biological control agents',
        'Remove heavily infested plant parts',
        'Maintain ant control (ants protect mealybugs)',
        'Regular monitoring and early intervention'
    ],
    'Unknown Data': [
        'Unable to classify — not cacao-related or unclear',
        'Verify if the image is of a cacao pest',
        'Consult pest expert for confirmation',
        'Try uploading a clearer image'
    ],
    'Cocoa Pod Borer': [
        'Regular harvesting of ripe pods every 7-10 days',
        'Remove infested pods immediately',
        'Apply biological or chemical control as recommended',
        'Maintain farm cleanliness',
        'Use pheromone traps for monitoring'
    ]
}


# Import PyTorch
import torch
import torch.nn as nn
from torchvision.models import resnet18


def get_daily_scan_limits(request):
    """Get or initialize daily scan limits for guest users"""
    today = timezone.now().date().isoformat()
    session_key = f'guest_scans_{today}'
    
    if session_key not in request.session:
        request.session[session_key] = {
            'disease': 0,
            'pest': 0,
            'date': today
        }
        request.session.modified = True
    
    return request.session[session_key]

def update_scan_count(request, scan_type):
    """Update scan count for guest users"""
    today = timezone.now().date().isoformat()
    session_key = f'guest_scans_{today}'
    
    if session_key in request.session:
        request.session[session_key][scan_type] += 1
        request.session.modified = True
        return request.session[session_key]
    return None

def guest_dashboard(request):
    """Guest dashboard view"""
    scan_limits = get_daily_scan_limits(request)
    
    disease_remaining = max(0, 5 - scan_limits.get('disease', 0))
    pest_remaining = max(0, 5 - scan_limits.get('pest', 0))
    
    context = {
        'disease_remaining': disease_remaining,
        'pest_remaining': pest_remaining,
    }
    return render(request, 'guest/guest_dashboard.html', context)



def get_recommendations(result, model_type):
    """Get recommendations based on detection result"""
    if model_type == 'disease':
        recommendations = DISEASE_RECOMMENDATIONS.get(result, [])
    else:
        recommendations = PEST_RECOMMENDATIONS.get(result, [])
    
    return recommendations

def toggle_history(request):
    """Toggle history visibility"""
    if request.method == 'POST':
        # This would typically update user preferences in the database
        # For now, we'll use session storage
        show_history = request.session.get('show_history', True)
        request.session['show_history'] = not show_history
        
        return JsonResponse({
            'success': True,
            'show_history': not show_history
        })
    
    return JsonResponse({'success': False})

def scan_history_api(request):
    """API endpoint to fetch user's scan history"""
    if request.method == 'GET':
        try:
            user_id = str(request.user.id)
            
            # Get user's scans from Firestore
            user_scans = db.collection('scans').where(filter=FieldFilter('user_id', '==', user_id)).order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
            scans_data = []
            
            for scan in user_scans:
                scan_data = scan.to_dict()
                scan_data['id'] = scan.id
                scans_data.append(scan_data)
            
            return JsonResponse({
                'success': True,
                'scans': scans_data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def validate_image_file(image_file):
    """Validate uploaded image file"""
    try:
        # Check file size (5MB limit)
        if image_file.size > 5 * 1024 * 1024:
            return False, "Image file too large. Maximum size is 5MB."
        
        # Check file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
        if image_file.content_type not in allowed_types:
            return False, "Invalid file type. Only JPEG and PNG images are allowed."
        
        # Check if file is actually an image
        try:
            img = Image.open(image_file)
            img.verify()
            image_file.seek(0)  # Reset file pointer after verification
            
            # Additional check for image format
            if img.format not in ['JPEG', 'PNG']:
                return False, "Invalid image format. Only JPEG and PNG are supported."
            
            return True, "Valid image file"
        except Exception as e:
            logger.error(f"Image validation error: {e}")
            return False, "Invalid image file or corrupted image."
    
    except Exception as e:
        logger.error(f"Error in validate_image_file: {e}")
        return False, "Error validating image file."

@csrf_exempt
def guest_scan_image(request):
    """Handle image scanning for guest users"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    try:
        scan_type = request.POST.get('scan_type')
        if scan_type not in ['disease', 'pest']:
            return JsonResponse({'success': False, 'message': 'Invalid scan type'})
        
        # Check scan limits
        scan_limits = get_daily_scan_limits(request)
        remaining = 5 - scan_limits.get(scan_type, 0)
        
        if remaining <= 0:
            return JsonResponse({
                'success': False, 
                'message': f'Daily {scan_type} scan limit reached',
                'limit_reached': True
            })
        
        # Handle file upload
        if 'image' not in request.FILES:
            return JsonResponse({'success': False, 'message': 'No image uploaded'})
        
        image_file = request.FILES['image']
        
        # Validate image file
        is_valid, validation_message = validate_image_file(image_file)
        if not is_valid:
            return JsonResponse({'success': False, 'message': validation_message})
        
        # Create guest_scans directory if it doesn't exist
        guest_scans_dir = os.path.join(settings.MEDIA_ROOT, 'guest_scans')
        os.makedirs(guest_scans_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(image_file.name)[1].lower()
        if not file_extension:
            file_extension = '.jpg'
        
        file_name = f"guest_scan_{uuid.uuid4().hex}{file_extension}"
        file_path = os.path.join(guest_scans_dir, file_name)
        
        # Save the file temporarily
        try:
            with open(file_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)
            
            logger.info(f"Image saved temporarily: {file_path}")
            
            # Make prediction
            result, confidence = predict_image(file_path, scan_type)
            recommendations = get_recommendations(result, scan_type)
            
            # Update scan count
            update_scan_count(request, scan_type)
            scan_limits = get_daily_scan_limits(request)
            
            # Clean up temporary file
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Temporary file removed: {file_path}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to remove temporary file: {cleanup_error}")
            
            return JsonResponse({
                'success': True,
                'result': result,
                'confidence': confidence,
                'recommendations': recommendations,
                'scan_type': scan_type,
                'remaining_scans': {
                    'disease': max(0, 5 - scan_limits.get('disease', 0)),
                    'pest': max(0, 5 - scan_limits.get('pest', 0))
                }
            })
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Clean up file if error occurs
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as cleanup_error:
                logger.warning(f"Failed to remove temporary file after error: {cleanup_error}")
            
            return JsonResponse({
                'success': False, 
                'message': f'Error processing image: {str(e)}'
            })
    
    except Exception as e:
        logger.error(f"Error in guest_scan_image: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return JsonResponse({
            'success': False, 
            'message': f'Server error: {str(e)}'
        })

def reset_guest_scans(request):
    """Reset guest scan counts (for testing purposes)"""
    if request.method == 'POST':
        try:
            today = timezone.now().date().isoformat()
            session_key = f'guest_scans_{today}'
            
            if session_key in request.session:
                del request.session[session_key]
                request.session.modified = True
            
            return JsonResponse({'success': True, 'message': 'Scan counts reset'})
        except Exception as e:
            logger.error(f"Error resetting scan counts: {e}")
            return JsonResponse({'success': False, 'message': f'Error resetting scan counts: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def get_scan_history(request):
    """Get scan history for guest users (from session)"""
    try:
        today = timezone.now().date().isoformat()
        session_key = f'guest_scans_{today}'
        
        scan_data = request.session.get(session_key, {
            'disease': 0,
            'pest': 0,
            'date': today
        })
        
        return JsonResponse({
            'success': True,
            'scans_used': {
                'disease': scan_data.get('disease', 0),
                'pest': scan_data.get('pest', 0)
            },
            'remaining_scans': {
                'disease': max(0, 5 - scan_data.get('disease', 0)),
                'pest': max(0, 5 - scan_data.get('pest', 0))
            },
            'date': scan_data.get('date', today)
        })
    except Exception as e:
        logger.error(f"Error getting scan history: {e}")
        return JsonResponse({'success': False, 'message': f'Error getting scan history: {str(e)}'})

# Additional helper function for debugging
def test_model_loading(request):
    """Test model loading (for debugging)"""
    try:
        load_models()
        
        status = {
            'disease_model_loaded': disease_model is not None,
            'pest_model_loaded': pest_model is not None,
        }
        
        return JsonResponse({
            'success': True,
            'status': status,
            'message': 'Model loading test completed'
        })
    except Exception as e:
        logger.error(f"Error testing model loading: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error testing model loading: {str(e)}'
        })
#Guest Scan End

def guest_marketplace(request):
    """Simplified guest marketplace with login prompts"""
    try:
        # Use sample products for guests (no Firebase dependency)
        products = SAMPLE_PRODUCTS.copy()
        
        # Apply basic filters
        category = request.GET.get('category')
        search = request.GET.get('search')
        
        if category:
            products = [p for p in products if p.get('category', '').lower() == category.lower()]
        
        if search:
            search_lower = search.lower()
            products = [p for p in products if 
                       search_lower in p.get('name', '').lower() or 
                       search_lower in p.get('description', '').lower()]
        
        # Get unique categories for filter
        categories = list(set([p.get('category', '') for p in SAMPLE_PRODUCTS if p.get('category')]))
        
        context = {
            'products': products,
            'categories': categories,
            'current_category': category,
            'current_search': search,
            'total_products': len(products)
        }
        
    except Exception as e:
        print(f"Error in guest_marketplace: {e}")
        # Fallback context
        context = {
            'products': SAMPLE_PRODUCTS,
            'categories': ['Raw Materials', 'Fresh Produce', 'Processed'],
            'current_category': None,
            'current_search': None,
            'total_products': len(SAMPLE_PRODUCTS)
        }
    
    return render(request, 'guest/guest_marketplace.html', context)

def guest_farm_mapping(request):
    """Simplified guest farm mapping view"""
    # Sample farm data for guests (public information only)
    public_farms = [
   
    {
        'id': 1,
        'name': 'Barangay Poblacion Farm',
        'municipality': 'Victoria',
        'barangay': 'Poblacion',
        'area': 4.5,
        'trees': 10,
        'status': 'Active',
        'lat': 13.1375,
        'lng': 121.2410,
        'description': 'Primary cacao growing area with established farms',
        'contact': 'Brgy. Captain Juan Santos',
        'created_at': '2024-01-15',
        'images': [
            '/static/images/download (2).jpg',
            '/static/images/download (1).jpg',
            '/static/images/download (3).jpg'
        ]

    },
    {
        'id': 2,
        'name': 'San Vicente Cacao Farm',
        'municipality': 'Victoria',
        'barangay': 'San Vicente',
        'area': 3.2,
        'trees': 15,
        'status': 'Active',
        'lat': 13.1500,
        'lng': 121.2333,
        'description': 'Emerging farming community with modern techniques',
        'contact': 'Brgy. Captain Maria Cruz',
        'created_at': '2024-01-14',
        'images': [
            '/static/images/download (1).jpg',
            '/static/images/download.jpg'
        ]
    },
    {
        'id': 3,
        'name': 'Macatoc Cacao Farm',
        'municipality': 'Victoria',
        'barangay': 'Macatoc',
        'area': 8.5,
        'trees': 13,
        'status': 'Monitoring',
        'lat': 13.1440,
        'lng': 121.2320,
        'description': 'Large scale cacao production facility',
        'contact': 'Farm Manager Pedro Reyes',
        'created_at': '2024-01-13',
        'images': [
            '/static/images/download (3).jpg',
            '/static/images/download (2).jpg'
        ]
    }
]
    
    context = {
        'farms_data': public_farms,
        'total_farms': len(public_farms),
        'total_area': sum(farm['area'] for farm in public_farms),
        'total_trees': sum(farm['trees'] for farm in public_farms)
    }
    return render(request, 'guest/guest_farm_mapping.html', context)

def guest_marketplace(request):
    """Guest marketplace view - shows products but requires login for actions"""
    # Get filter parameters
    category = request.GET.get('category')
    product_type = request.GET.get('type')
    search = request.GET.get('search')
    sort_by = request.GET.get('sort', 'name')
    
    # Get products from Firestore
    products = firestore_service.get_products()
    
    # Filter products
    if category:
        products = [p for p in products if p.get('category') == category]
    
    if product_type:
        products = [p for p in products if p.get('product_type') == product_type]
    
    if search:
        products = [p for p in products if search.lower() in p.get('name', '').lower() or 
                   search.lower() in p.get('description', '').lower()]
    
    # Sort products
    if sort_by == 'price_low':
        products.sort(key=lambda x: x.get('price', 0))
    elif sort_by == 'price_high':
        products.sort(key=lambda x: x.get('price', 0), reverse=True)
    elif sort_by == 'newest':
        products.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    # Get categories for filter
    categories = list(set([p.get('category') for p in products if p.get('category')]))
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': category,
        'current_type': product_type,
        'current_search': search,
        'current_sort': sort_by,
        'product_types': [
            ('fresh_cacao', 'Fresh Cacao Fruit'),
            ('dried_beans', 'Dried Cacao Beans'),
            ('cacao_powder', 'Cacao Powder'),
            ('chocolate', 'Chocolate Products'),
            ('cacao_butter', 'Cacao Butter'),
            ('cacao_nibs', 'Cacao Nibs'),
        ]
    }
    
    return render(request, 'guest/guest_marketplace.html', context)

def guest_product_detail(request, product_id):
    """Guest product detail view"""
    product = firestore_service.get_product(product_id)
    if not product:
        messages.error(request, 'Product not found.')
        return redirect('guest_marketplace')
    
    # Get related products
    related_products = firestore_service.get_products(limit=4)
    related_products = [p for p in related_products if p.get('id') != product_id][:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    
    return render(request, 'guest/product_detail.html', context)

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from .decorators import admin_required, user_required
import json
from datetime import datetime
import uuid
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

# Initialize Firestore

# ===============================
# USER ORDERS
# ===============================

@user_required
def user_orders(request):
    """Display user's orders from Firestore (excluding hidden orders)"""
    try:
        uid = request.session.get('uid')
        if not uid:
            messages.error(request, 'Please log in to view your orders.')
            return redirect('login')

        # Get all orders for this user first
        orders_ref = db.collection('orders')
        query = orders_ref.where('firebase_uid', '==', uid).order_by('created_at', direction=firestore.Query.DESCENDING)

        orders_data = []
        for doc in query.stream():
            order_data = doc.to_dict()
            order_data['id'] = doc.id
            
            # Skip hidden orders (check if hidden field exists and is True)
            if order_data.get('hidden', False):
                continue
            
            # Convert Firestore timestamp to datetime if needed
            if 'created_at' in order_data and order_data['created_at']:
                if hasattr(order_data['created_at'], 'seconds'):
                    order_data['created_at'] = datetime.fromtimestamp(order_data['created_at'].seconds, tz=pytz.UTC).astimezone(pytz.timezone('Asia/Manila'))
            
            # Calculate total items
            order_data['total_items'] = len(order_data.get('items', []))
            
            orders_data.append(order_data)

        # Calculate statistics
        total_orders = len(orders_data)
        pending_orders = len([o for o in orders_data if o.get('status') == 'pending'])
        delivered_orders = len([o for o in orders_data if o.get('status') == 'delivered'])
        total_spent = sum(float(o.get('total_amount', 0)) for o in orders_data if o.get('status') == 'delivered')

        context = {
            'orders': orders_data,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'delivered_orders': delivered_orders,
            'total_spent': total_spent,
            'user_email': request.session.get('user_email', 'User'),
        }

        return render(request, 'user/orders.html', context)

    except Exception as e:
        print(f"Error fetching user orders: {str(e)}")
        messages.error(request, 'Error loading orders. Please try again.')
        return render(request, 'user/orders.html', {'orders': []})
    
@user_required
def order_detail(request, order_id):
    """Order detail view for users"""
    try:
        uid = request.session.get('uid')
        if not uid:
            messages.error(request, 'Please log in to view order details.')
            return redirect('login')

        # Get specific order from Firestore
        order_ref = db.collection('orders').document(order_id)
        order_doc = order_ref.get()

        if not order_doc.exists:
            messages.error(request, 'Order not found.')
            return redirect('user_orders')

        order_data = order_doc.to_dict()
        
        # Check if order belongs to current user
        if order_data.get('firebase_uid') != uid:
            messages.error(request, 'Access denied.')
            return redirect('user_orders')

        order_data['id'] = order_doc.id
        
        # Convert timestamp if needed
        # NEW (shows correct Philippines time)
        if hasattr(order_data['created_at'], 'seconds'):
            utc_time = datetime.fromtimestamp(order_data['created_at'].seconds, tz=pytz.UTC)
            philippines_tz = pytz.timezone('Asia/Manila')
            order_data['created_at'] = utc_time.astimezone(philippines_tz)

        context = {
            'order': order_data,
        }

        return render(request, 'user/order_detail.html', context)

    except Exception as e:
        print(f"Error fetching order detail: {str(e)}")
        messages.error(request, 'Error loading order details.')
        return redirect('user_orders')

# ===============================
# ADMIN ORDER MANAGEMENT
# ===============================

@admin_required
def admin_orders(request):
    """Admin orders management with Firestore"""
    try:
        # Get filter parameters
        status_filter = request.GET.get('status', '')
        search = request.GET.get('search', '')
        date_filter = request.GET.get('date', '')

        # Base query
        orders_ref = db.collection('orders')
        
        # Apply status filter
        if status_filter:
            query = orders_ref.where('status', '==', status_filter)
        else:
            query = orders_ref
            
        # Order by creation date
        query = query.order_by('created_at', direction=firestore.Query.DESCENDING)

        orders_data = []
        for doc in query.stream():
            order_data = doc.to_dict()
            order_data['id'] = doc.id
            
            # Convert timestamp
            if 'created_at' in order_data and order_data['created_at']:
                if hasattr(order_data['created_at'], 'seconds'):
                    order_data['created_at'] = datetime.fromtimestamp(order_data['created_at'].seconds, tz=pytz.UTC).astimezone(pytz.timezone('Asia/Manila'))
            
            # Apply search filter
            if search:
                search_lower = search.lower()
                if not (search_lower in order_data.get('order_id', '').lower() or 
                       search_lower in order_data.get('customer_email', '').lower() or
                       search_lower in order_data.get('customer_name', '').lower()):
                    continue
            
            # Apply date filter
            if date_filter and 'created_at' in order_data:
                try:
                    filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                    if order_data['created_at'].date() != filter_date:
                        continue
                except:
                    pass
            
            # Calculate total items
            order_data['total_items'] = len(order_data.get('items', []))
            
            orders_data.append(order_data)

        # Calculate statistics
        all_orders = list(db.collection('orders').stream())
        total_orders = len(all_orders)
        pending_orders = len([o for o in all_orders if o.to_dict().get('status') == 'pending'])
        confirmed_orders = len([o for o in all_orders if o.to_dict().get('status') == 'confirmed'])
        shipped_orders = len([o for o in all_orders if o.to_dict().get('status') == 'shipped'])
        delivered_orders = len([o for o in all_orders if o.to_dict().get('status') == 'delivered'])
        cancelled_orders = len([o for o in all_orders if o.to_dict().get('status') == 'cancelled'])

        # Pagination
        page = request.GET.get('page', 1)
        try:
            page = int(page)
        except:
            page = 1
        
        items_per_page = 10
        start_index = (page - 1) * items_per_page
        end_index = start_index + items_per_page
        paginated_orders = orders_data[start_index:end_index]
        
        total_pages = (len(orders_data) + items_per_page - 1) // items_per_page
        has_previous = page > 1
        has_next = page < total_pages

        context = {
            'orders': paginated_orders,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'confirmed_orders': confirmed_orders,
            'shipped_orders': shipped_orders,
            'delivered_orders': delivered_orders,
            'cancelled_orders': cancelled_orders,
            'current_page': page,
            'total_pages': total_pages,
            'has_previous': has_previous,
            'has_next': has_next,
            'previous_page': page - 1 if has_previous else None,
            'next_page': page + 1 if has_next else None,
            'filters': {
                'status': status_filter,
                'search': search,
                'date': date_filter
            },
            'status_choices': [
                ('pending', 'Pending'),
                ('confirmed', 'Confirmed'),
                ('processing', 'Processing'),
                ('shipped', 'Shipped'),
                ('delivered', 'Delivered'),
                ('cancelled', 'Cancelled'),
            ]
        }

        return render(request, 'admin/orders.html', context)

    except Exception as e:
        print(f"Error in admin_orders: {str(e)}")
        messages.error(request, f'Error loading orders: {str(e)}')
        return render(request, 'admin/orders.html', {'orders': []})

@admin_required
def admin_order_detail(request, order_id):
    """Admin order detail view"""
    try:
        # Get specific order from Firestore
        order_ref = db.collection('orders').document(order_id)
        order_doc = order_ref.get()

        if not order_doc.exists:
            messages.error(request, 'Order not found.')
            return redirect('admin_orders')

        order_data = order_doc.to_dict()
        order_data['id'] = order_doc.id
        
        # Convert timestamp
        if 'created_at' in order_data and order_data['created_at']:
            if hasattr(order_data['created_at'], 'seconds'):
                order_data['created_at'] = datetime.fromtimestamp(order_data['created_at'].seconds, tz=pytz.UTC).astimezone(pytz.timezone('Asia/Manila'))

        # Handle status update
        if request.method == 'POST':
            new_status = request.POST.get('status')
            if new_status:
                try:
                    # Update status in Firestore
                    order_ref.update({
                        'status': new_status,
                        'updated_at': firestore.SERVER_TIMESTAMP
                    })
                    
                    messages.success(request, f'Order status updated to {new_status}')
                    return redirect('admin_order_detail', order_id=order_id)
                except Exception as e:
                    messages.error(request, f'Error updating status: {str(e)}')

        context = {
            'order': order_data,
            'status_choices': [
                ('pending', 'Pending'),
                ('confirmed', 'Confirmed'),
                ('processing', 'Processing'),
                ('shipped', 'Shipped'),
                ('delivered', 'Delivered'),
                ('cancelled', 'Cancelled'),
            ]
        }

        return render(request, 'admin/admin_order_detail.html', context)

    except Exception as e:
        print(f"Error in admin_order_detail: {str(e)}")
        messages.error(request, 'Error loading order details.')
        return redirect('admin_orders')

@admin_required
@csrf_exempt
def update_order_status(request):
    """API endpoint to update order status"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            new_status = data.get('status')

            if not order_id or not new_status:
                return JsonResponse({
                    'success': False,
                    'message': 'Order ID and status are required'
                })

            # Update in Firestore
            order_ref = db.collection('orders').document(order_id)
            order_ref.update({
                'status': new_status,
                'updated_at': firestore.SERVER_TIMESTAMP
            })

            return JsonResponse({
                'success': True,
                'message': f'Order status updated to {new_status}'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

@admin_required
@csrf_exempt
def delete_order(request, order_id):
    """Delete order (admin only)"""
    if request.method == 'POST':
        try:
            # Delete from Firestore
            db.collection('orders').document(order_id).delete()
            messages.success(request, 'Order deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting order: {str(e)}')
    
    return redirect('admin_orders')

# ===============================
# ENHANCED CHECKOUT WITH FIRESTORE
# ===============================

def checkout_view(request):
    """Enhanced checkout process with Firestore integration"""
    
    # Check Firebase authentication using session data
    uid = request.session.get('uid')
    user_email = request.session.get('user_email')
    user_name = request.session.get('name')
    user_role = request.session.get('role')
    
    # Check if user is authenticated
    if not uid or not user_email:
        messages.error(request, 'Please log in to proceed with checkout.')
        request.session['checkout_redirect'] = True
        return redirect('login')
    
    cart_items_data = request.session.get('cart', [])
    
    if not cart_items_data:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart_view')
    
    # Get detailed cart items (you'll need to implement get_product_from_firestore)
    cart_items = []
    total_amount = 0
    
    for item_data in cart_items_data:
        try:
            # Get product data from your product source (Firestore or sample data)
            product_data = get_product_by_id(item_data['product_id'])
            if product_data:
                item_total = float(product_data.get('price', 0)) * item_data['quantity']
                cart_items.append({
                    'product': product_data,
                    'quantity': item_data['quantity'],
                    'total_price': item_total
                })
                total_amount += item_total
        except Exception as e:
            print(f"Error getting product {item_data['product_id']}: {str(e)}")
            continue
    
    if not cart_items:
        messages.error(request, 'Unable to load cart items. Please try again.')
        return redirect('cart_view')
    
    if request.method == 'POST':
        # Process order
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        shipping_address = request.POST.get('shipping_address', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        notes = request.POST.get('notes', '').strip()
        payment_method = request.POST.get('payment_method', 'cod')
        
        # Pre-fill email with logged-in user's email if not provided
        if not email:
            email = user_email
        
        # Validate required fields
        if not all([first_name, last_name, email, shipping_address, phone_number]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'user/checkout.html', {
                'cart_items': cart_items,
                'total': total_amount,
                'user_name': user_name,
                'user_email': user_email,
            })
        
        try:
            # Generate unique order ID
            order_id = str(uuid.uuid4())[:8].upper()
            
            # Prepare order items data
            order_items_data = []
            for item in cart_items:
                order_items_data.append({
                    'product_id': item['product']['id'],
                    'product_name': item['product']['name'],
                    'quantity': item['quantity'],
                    'price': float(item['product']['price']),
                    'total_price': item['total_price']
                })
            
            # Create order data for Firestore
            order_data = {
                'order_id': order_id,
                'firebase_uid': uid,
                'customer_first_name': first_name,
                'customer_last_name': last_name,
                'customer_email': email,
                'customer_name': user_name,
                'status': 'pending',
                'total_amount': float(total_amount),
                'shipping_address': shipping_address,
                'phone_number': phone_number,
                'notes': notes,
                'payment_method': payment_method,
                'items': order_items_data,
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP,
                'order_date': datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Save order to Firestore
            doc_ref = db.collection('orders').add(order_data)

            # Add this code block right after: doc_ref = db.collection('orders').add(order_data)

            # Reduce stock quantities
            for item in cart_items:
                product_id = item['product']['id']
                quantity_ordered = item['quantity']
                
                # Find and update product in SAMPLE_PRODUCTS
                for i, product in enumerate(SAMPLE_PRODUCTS):
                    if str(product['id']) == str(product_id):
                        current_stock = product.get('stock_quantity', 0)
                        new_stock = max(0, current_stock - quantity_ordered)  # Don't go below 0
                        SAMPLE_PRODUCTS[i]['stock_quantity'] = new_stock
                        print(f"Updated stock for {product['name']}: {current_stock} -> {new_stock}")
                        break

            # Clear cart
            request.session['cart'] = []
            request.session.modified = True
            
            # Store order ID in session for confirmation page
            request.session['last_order_id'] = order_id
            
            messages.success(request, f'Order placed successfully! Order ID: {order_id}')
            
            # Redirect to order confirmation
            return redirect('order_confirmation', order_id=order_id)
            
        except Exception as e:
            print(f"Order creation error: {str(e)}")
            messages.error(request, f'Error processing order: {str(e)}')
    
    # Pre-fill form with user data
    form_data = {
        'email': user_email,
        'first_name': user_name.split(' ')[0] if user_name else '',
        'last_name': ' '.join(user_name.split(' ')[1:]) if user_name and len(user_name.split(' ')) > 1 else ''
    }
    
    context = {
        'cart_items': cart_items,
        'total': total_amount,
        'user_name': user_name,
        'user_email': user_email,
        'user_role': user_role,
        'form_data': form_data
    }
    
    return render(request, 'user/checkout.html', context)

import pytz
def order_confirmation(request, order_id):
    """Order confirmation page"""
    
    # Check if user is logged in
    uid = request.session.get('uid')
    if not uid:
        messages.error(request, 'Please log in to view your order.')
        return redirect('login')
    
    try:
        # Get order from Firestore by order_id field
        orders_ref = db.collection('orders')
        query = orders_ref.where('order_id', '==', order_id).limit(1)
        docs = list(query.stream())
        
        if not docs:
            messages.error(request, 'Order not found.')
            return redirect('userdashboard')
        
        order_data = docs[0].to_dict()
        order_data['id'] = docs[0].id
        
        # Check if order belongs to current user
        if order_data.get('firebase_uid') != uid:
            messages.error(request, 'Access denied.')
            return redirect('userdashboard')
        
        # Convert timestamp
        # NEW (shows correct Philippines time)
        if hasattr(order_data['created_at'], 'seconds'):
            utc_time = datetime.fromtimestamp(order_data['created_at'].seconds, tz=pytz.UTC)
            philippines_tz = pytz.timezone('Asia/Manila')
            order_data['created_at'] = utc_time.astimezone(philippines_tz)
        
        # ADD SUCCESS MESSAGE
        messages.success(request, f'Order #{order_id} placed successfully! Please wait for admin confirmation.')
        
        context = {
            'order': order_data,
            'order_id': order_id,
            'user_name': request.session.get('name'),
            'user_email': request.session.get('user_email')
        }
        
        return render(request, 'user/order_confirmation.html', context)
        
    except Exception as e:
        print(f"Error loading order confirmation: {str(e)}")
        messages.error(request, 'Error loading order details.')
        return redirect('user_orders')

# Helper function to get product by ID
def get_product_by_id(product_id):
    """Get product by ID from your data source"""
    # First try to get from your sample products
    for product in SAMPLE_PRODUCTS:
        if str(product['id']) == str(product_id):
            return product
    
    # If not found in sample products, try Firestore (if you have products there)
    try:
        if db:
            product_ref = db.collection('products').document(str(product_id))
            product_doc = product_ref.get()
            if product_doc.exists:
                product_data = product_doc.to_dict()
                product_data['id'] = product_doc.id
                return product_data
    except Exception as e:
        print(f"Error getting product from Firestore: {e}")
    
    return None

# Sample products data (you already have this)
SAMPLE_PRODUCTS = [
    {
        'id': '1',
        'name': 'Premium Cacao Beans',
        'description': 'High-quality dried cacao beans from Victoria, Oriental Mindoro',
        'price': 250.00,
        'stock_quantity': 50,
        'category': 'Raw Materials',
        'product_type': 'dried_beans',
        'images': ['/static/images/cacao-beans.jpg'],
        'is_active': True,
        'featured': True,
        'origin': 'Victoria, Oriental Mindoro',
        'unit': 'kg'
    },
    # Add more sample products as needed
]

@user_required
@csrf_exempt
def cancel_order(request, order_id):
    """Cancel user order"""
    if request.method == 'POST':
        try:
            uid = request.session.get('uid')
            if not uid:
                return JsonResponse({'success': False, 'message': 'Please log in'})

            # Get order from Firestore
            order_ref = db.collection('orders').document(order_id)
            order_doc = order_ref.get()

            if not order_doc.exists:
                return JsonResponse({'success': False, 'message': 'Order not found'})

            order_data = order_doc.to_dict()
            
            # Check if order belongs to current user
            if order_data.get('firebase_uid') != uid:
                return JsonResponse({'success': False, 'message': 'Access denied'})
            
            # Check if order can be cancelled (only pending orders)
            if order_data.get('status') != 'pending':
                return JsonResponse({'success': False, 'message': 'Order cannot be cancelled'})

            # Update order status to cancelled
            order_ref.update({
                'status': 'cancelled',
                'updated_at': firestore.SERVER_TIMESTAMP
            })

            # Restore stock quantities
            for item in order_data.get('items', []):
                product_id = item.get('product_id')
                quantity = item.get('quantity', 0)
                
                # Find and update product in SAMPLE_PRODUCTS
                for i, product in enumerate(SAMPLE_PRODUCTS):
                    if str(product['id']) == str(product_id):
                        current_stock = product.get('stock_quantity', 0)
                        new_stock = current_stock + quantity
                        SAMPLE_PRODUCTS[i]['stock_quantity'] = new_stock
                        break

            return JsonResponse({'success': True, 'message': 'Order cancelled successfully'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@user_required
@csrf_exempt
def hide_order(request, order_id):
    """Hide order from user's view"""
    if request.method == 'POST':
        try:
            uid = request.session.get('uid')
            if not uid:
                return JsonResponse({
                    'success': False,
                    'message': 'Please log in to perform this action.'
                })

            # Get order from Firestore
            order_ref = db.collection('orders').document(order_id)
            order_doc = order_ref.get()

            if not order_doc.exists:
                return JsonResponse({
                    'success': False,
                    'message': 'Order not found.'
                })

            order_data = order_doc.to_dict()
            
            # Check if order belongs to current user
            if order_data.get('firebase_uid') != uid:
                return JsonResponse({
                    'success': False,
                    'message': 'Access denied.'
                })

            # Update order to hidden
            order_ref.update({
                'hidden': True,
                'hidden_at': firestore.SERVER_TIMESTAMP
            })

            return JsonResponse({
                'success': True,
                'message': 'Order hidden successfully.'
            })

        except Exception as e:
            print(f"Error hiding order: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error hiding order: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

@user_required
@csrf_exempt
def delete_user_order(request, order_id):
    """Delete order (only for cancelled or delivered orders)"""
    if request.method == 'POST':
        try:
            uid = request.session.get('uid')
            if not uid:
                return JsonResponse({
                    'success': False,
                    'message': 'Please log in to perform this action.'
                })

            # Get order from Firestore
            order_ref = db.collection('orders').document(order_id)
            order_doc = order_ref.get()

            if not order_doc.exists:
                return JsonResponse({
                    'success': False,
                    'message': 'Order not found.'
                })

            order_data = order_doc.to_dict()
            
            # Check if order belongs to current user
            if order_data.get('firebase_uid') != uid:
                return JsonResponse({
                    'success': False,
                    'message': 'Access denied.'
                })

            # Check if order can be deleted (only cancelled or delivered orders)
            if order_data.get('status') not in ['cancelled', 'delivered']:
                return JsonResponse({
                    'success': False,
                    'message': 'Only cancelled or delivered orders can be deleted.'
                })

            # Delete order from Firestore
            order_ref.delete()

            return JsonResponse({
                'success': True,
                'message': 'Order deleted successfully.'
            })

        except Exception as e:
            print(f"Error deleting order: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error deleting order: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

@user_required
def hidden_orders(request):
    """Display user's hidden orders from Firestore"""
    try:
        uid = request.session.get('uid')
        if not uid:
            messages.error(request, 'Please log in to view your orders.')
            return redirect('login')

        # Get ALL orders from Firestore for this user first
        orders_ref = db.collection('orders')
        query = orders_ref.where('firebase_uid', '==', uid).order_by('created_at', direction=firestore.Query.DESCENDING)
        
        orders_data = []
        for doc in query.stream():
            order_data = doc.to_dict()
            order_data['id'] = doc.id
            
            # Only include hidden orders (check if hidden field exists and is True)
            if not order_data.get('hidden', False):
                continue
            
            # Convert Firestore timestamp to datetime if needed
            if 'created_at' in order_data and order_data['created_at']:
                if hasattr(order_data['created_at'], 'seconds'):
                    order_data['created_at'] = datetime.fromtimestamp(order_data['created_at'].seconds, tz=pytz.UTC).astimezone(pytz.timezone('Asia/Manila'))
            
            # Calculate total items
            order_data['total_items'] = len(order_data.get('items', []))
            
            orders_data.append(order_data)

        # Calculate statistics for hidden orders
        total_hidden_orders = len(orders_data)
        total_spent_hidden = sum(float(o.get('total_amount', 0)) for o in orders_data)

        print(f"Found {total_hidden_orders} hidden orders for user {uid}")  # Debug line

        context = {
            'orders': orders_data,
            'total_hidden_orders': total_hidden_orders,
            'total_spent_hidden': total_spent_hidden,
            'user_email': request.session.get('user_email', 'User'),
        }

        return render(request, 'user/hidden_orders.html', context)

    except Exception as e:
        print(f"Error fetching hidden orders: {str(e)}")
        messages.error(request, 'Error loading hidden orders. Please try again.')
        return render(request, 'user/hidden_orders.html', {'orders': []})

@user_required
@csrf_exempt
def unhide_order(request, order_id):
    """Unhide order (make it visible again)"""
    if request.method == 'POST':
        try:
            uid = request.session.get('uid')
            if not uid:
                return JsonResponse({
                    'success': False,
                    'message': 'Please log in to perform this action.'
                })

            # Get order from Firestore
            order_ref = db.collection('orders').document(order_id)
            order_doc = order_ref.get()

            if not order_doc.exists:
                return JsonResponse({
                    'success': False,
                    'message': 'Order not found.'
                })

            order_data = order_doc.to_dict()
            
            # Check if order belongs to current user
            if order_data.get('firebase_uid') != uid:
                return JsonResponse({
                    'success': False,
                    'message': 'Access denied.'
                })

            # Update order to unhidden
            order_ref.update({
                'hidden': False,
                'unhidden_at': firestore.SERVER_TIMESTAMP
            })

            return JsonResponse({
                'success': True,
                'message': 'Order restored successfully.'
            })

        except Exception as e:
            print(f"Error unhiding order: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error restoring order: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })


from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .decorators import user_required
import json
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
import pytz

# Initialize Firestore

@user_required
def userdashboard(request):
    """Enhanced User Dashboard with comprehensive analytics"""
    print("[DEBUG] Accessing User Dashboard:", request.session.get('user_email'), request.session.get('role'))
        
    if request.session.get('role') == 'guest':
        messages.error(request, "Guest users cannot access user dashboard.")
        return redirect('guest_dashboard')
        
    uid = request.session.get('uid')
    user_email = request.session.get('user_email')
        
    try:
        # ===== FETCH ORDERS DATA =====
        orders_ref = db.collection('orders')
        user_orders_query = orders_ref.where('firebase_uid', '==', uid)
        user_orders = list(user_orders_query.stream())
        total_orders = len(user_orders)
        pending_orders = len([o for o in user_orders if o.to_dict().get('status') == 'pending'])
        delivered_orders = len([o for o in user_orders if o.to_dict().get('status') == 'delivered'])
        total_spent = sum(float(o.to_dict().get('total_amount', 0)) for o in user_orders if o.to_dict().get('status') == 'delivered')

        # Recent orders for display
        recent_orders = []
        for doc in sorted(user_orders, key=lambda x: x.to_dict().get('created_at', datetime.now(pytz.timezone('Asia/Manila'))), reverse=True)[:5]:
            order_data = doc.to_dict()
            order_data['id'] = doc.id
            if 'created_at' in order_data and order_data['created_at']:
                if hasattr(order_data['created_at'], 'seconds'):
                    order_data['created_at'] = datetime.fromtimestamp(order_data['created_at'].seconds, tz=pytz.UTC).astimezone(pytz.timezone('Asia/Manila')),
            recent_orders.append(order_data)
                
        # ===== FETCH SCANS DATA =====
        scans_ref = db.collection('scans')
        user_scans_query = scans_ref.where('user_id', '==', uid)
        user_scans = list(user_scans_query.stream())
                
        total_scans = len(user_scans)
        disease_scans = len([s for s in user_scans if s.to_dict().get('type') == 'disease'])
        pest_scans = len([s for s in user_scans if s.to_dict().get('type') == 'pest'])
                
        # Recent scans for display
        recent_scans = []
        for doc in sorted(user_scans, key=lambda x: x.to_dict().get('timestamp', datetime.now(pytz.timezone('Asia/Manila'))), reverse=True)[:5]:
            scan_data = doc.to_dict()
            scan_data['id'] = doc.id
            if 'timestamp' in scan_data and scan_data['timestamp']:
                if hasattr(scan_data['timestamp'], 'seconds'):
                    scan_data['timestamp'] = datetime.fromtimestamp(scan_data['timestamp'].seconds)
            recent_scans.append(scan_data)
                
        # ===== FETCH FARM MAPS DATA (FIXED) =====
        # Start with sample farms
        total_farm_area = sum(farm.get('area', 0) for farm in SAMPLE_FARMS)
        total_trees = sum(farm.get('trees', 0) for farm in SAMPLE_FARMS)
        total_maps = len(SAMPLE_FARMS)
        
        # Add Firebase farms data
        try:
            farms_ref = db.collection('farms')
            firebase_farms = list(farms_ref.stream())
            
            # Add Firebase farms to totals
            for farm_doc in firebase_farms:
                farm_data = farm_doc.to_dict()
                total_farm_area += float(farm_data.get('area', 0))
                total_trees += int(farm_data.get('trees', 0))
            
            total_maps += len(firebase_farms)
            
            print(f"[DEBUG] Farm totals - Maps: {total_maps}, Area: {total_farm_area}, Trees: {total_trees}")
            print(f"[DEBUG] Sample farms: {len(SAMPLE_FARMS)}, Firebase farms: {len(firebase_farms)}")
            
        except Exception as farm_error:
            print(f"[ERROR] Error fetching Firebase farms: {farm_error}")
            # Continue with just sample farms data
            pass
                
        # ===== PREPARE CHART DATA =====
        # Orders chart data (last 7 days)
        tz = pytz.timezone('Asia/Manila')
        today = datetime.now(tz)
        orders_chart_data = []
        scans_chart_data = []
                
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
                        
            # Count orders for this date
            daily_orders = len([
                o for o in user_orders 
                if o.to_dict().get('created_at') and
                o.to_dict()['created_at'].astimezone(tz).date() == date.date()
            ])
                        
            # Count scans for this date
            daily_scans = len([
                s for s in user_scans 
                if s.to_dict().get('timestamp') and
                s.to_dict()['timestamp'].astimezone(tz).date() == date.date()
            ])
                        
            orders_chart_data.append({
                'date': date_str,
                'count': daily_orders,
                'label': date.strftime('%b %d')
            })
                        
            scans_chart_data.append({
                'date': date_str,
                'count': daily_scans,
                'label': date.strftime('%b %d')
            })
                
        # Scan type distribution for pie chart
        scan_distribution = {
            'disease': disease_scans,
            'pest': pest_scans
        }
                
        context = {
            'name': request.session.get('name'),
            'email': user_email,
            'role': request.session.get('role'),
            'uid': uid,
                        
            # Main totals for your existing cards
            'total_orders': total_orders,
            'total_scans': total_scans,
            'total_maps': total_maps,
                        
            # Additional detailed stats
            'pending_orders': pending_orders,
            'delivered_orders': delivered_orders,
            'total_spent': round(total_spent, 2),
            'disease_scans': disease_scans,
            'pest_scans': pest_scans,
            
            # FIXED: Now includes both sample and Firebase farms
            'total_farm_area': round(total_farm_area, 1),  # Round to 1 decimal place
            'total_trees': total_trees,
                        
            # Recent data for activity sections
            'recent_orders': recent_orders,
            'recent_scans': recent_scans,
            'recent_farms': SAMPLE_FARMS[:3],
                        
            # Chart data
            'orders_chart_data': json.dumps(orders_chart_data),
            'scans_chart_data': json.dumps(scans_chart_data),
            'scan_distribution': json.dumps(scan_distribution),
                        
            # Current date/time
            'current_date': today.strftime('%Y-%m-%d'),
            'current_time': today.strftime('%H:%M:%S'),
        }
            
    except Exception as e:
        print(f"Error in userdashboard: {str(e)}")
        
        # Fallback data if Firebase fails - but still try to get Firebase farms
        fallback_area = sum(farm.get('area', 0) for farm in SAMPLE_FARMS)
        fallback_trees = sum(farm.get('trees', 0) for farm in SAMPLE_FARMS)
        fallback_maps = len(SAMPLE_FARMS)
        
        # Try to add Firebase farms even in fallback
        try:
            farms_ref = db.collection('farms')
            firebase_farms = list(farms_ref.stream())
            for farm_doc in firebase_farms:
                farm_data = farm_doc.to_dict()
                fallback_area += float(farm_data.get('area', 0))
                fallback_trees += int(farm_data.get('trees', 0))
            fallback_maps += len(firebase_farms)
        except:
            pass
        
        context = {
            'name': request.session.get('name'),
            'email': user_email,
            'role': request.session.get('role'),
            'uid': uid,
            'total_orders': 0,
            'total_scans': 0,
            'total_maps': fallback_maps,
            'pending_orders': 0,
            'delivered_orders': 0,
            'total_spent': 0,
            'disease_scans': 0,
            'pest_scans': 0,
            
            # FIXED: Fallback also includes Firebase farms
            'total_farm_area': round(fallback_area, 1),
            'total_trees': fallback_trees,
            
            'recent_orders': [],
            'recent_scans': [],
            'recent_farms': SAMPLE_FARMS[:3],
            'orders_chart_data': json.dumps([]),
            'scans_chart_data': json.dumps([]),
            'scan_distribution': json.dumps({'disease': 0, 'pest': 0}),
            'current_date': datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d'),
            'current_time': datetime.now(pytz.timezone('Asia/Manila')).strftime('%H:%M:%S'),
        }
        
    return render(request, 'user/userdashboard.html', context)
# End userdashboard


@user_required
@csrf_exempt
def dashboard_api(request):
    """API endpoint for real-time dashboard updates"""
    if request.method == 'GET':
        uid = request.session.get('uid')
        
        try:
            # Get latest counts
            orders_count = len(list(db.collection('orders').where('firebase_uid', '==', uid).stream()))
            scans_count = len(list(db.collection('scans').where('user_id', '==', uid).stream()))
            maps_count = len(SAMPLE_FARMS)
            
            # Add Firebase farms count
            try:
                firebase_farms = list(db.collection('farms').stream())
                maps_count += len(firebase_farms)
            except:
                pass
            
            return JsonResponse({
                'success': True,
                'data': {
                    'total_orders': orders_count,
                    'total_scans': scans_count,
                    'total_maps': maps_count,
                    'timestamp': datetime.now(pytz.timezone('Asia/Manila')).isoformat()
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@user_required
def generate_dashboard_report(request):
    """Generate printable dashboard report"""
    uid = request.session.get('uid')
    user_email = request.session.get('user_email')
    
    try:
        # Fetch all user data
        orders_ref = db.collection('orders')
        user_orders = list(orders_ref.where('firebase_uid', '==', uid).stream())
        
        scans_ref = db.collection('scans')
        user_scans = list(scans_ref.where('user_id', '==', uid).stream())
        
        # Prepare report data
        report_data = {
            'user_name': request.session.get('name'),
            'user_email': user_email,
            'generated_at': datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S'),
            'total_orders': len(user_orders),
            'total_scans': len(user_scans),
            'total_maps': len(SAMPLE_FARMS),
            'orders_summary': {
                'pending': len([o for o in user_orders if o.to_dict().get('status') == 'pending']),
                'delivered': len([o for o in user_orders if o.to_dict().get('status') == 'delivered']),
                'cancelled': len([o for o in user_orders if o.to_dict().get('status') == 'cancelled']),
            },
            'scans_summary': {
                'disease': len([s for s in user_scans if s.to_dict().get('type') == 'disease']),
                'pest': len([s for s in user_scans if s.to_dict().get('type') == 'pest']),
            }
        }
        
        return render(request, 'user/dashboard_report.html', {'report': report_data})
        
    except Exception as e:
        messages.error(request, f'Error generating report: {str(e)}')
        return redirect('userdashboard')


import os
import json
import uuid
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import resnet18
import numpy as np
from PIL import Image
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
import pytz
from .decorators import admin_required, user_required

# Firebase and Firestore already initialized in firebase_config module

# ===============================
# MODEL DEFINITIONS
# ===============================
class CacaoResNet(nn.Module):
    def __init__(self, num_classes):
        super(CacaoResNet, self).__init__()
        self.resnet = resnet18(weights=None)
        in_features = self.resnet.fc.in_features
        self.resnet.fc = nn.Linear(in_features, num_classes)

    def forward(self, x):
        return self.resnet(x)

def load_pytorch_model(model_path, model_class, num_classes):
    try:
        model = model_class(num_classes=num_classes)
        state_dict = torch.load(model_path, map_location="cpu")

        # Fix key mismatch by adding "resnet." prefix if missing
        new_state_dict = {}
        for k, v in state_dict.items():
            if not k.startswith("resnet."):
                new_state_dict["resnet." + k] = v
            else:
                new_state_dict[k] = v

        model.load_state_dict(new_state_dict, strict=False)
        model.eval()
        print(f"Successfully loaded PyTorch model: {model_path}")
        return model
    except Exception as e:
        print(f"Error loading PyTorch model {model_path}: {e}")
        return None

# Load your models (PyTorch only)
# Both checkpoints were trained with 5 classes
disease_model = load_pytorch_model(
    "models/cacao_disease_resnet_state_dict.pth",
    CacaoResNet,
    num_classes=5
)

pest_model = load_pytorch_model(
    "models/cacao_pest_resnet_state_dict.pth",
    CacaoResNet,
    num_classes=5
)

# ===============================
# IMAGE PREPROCESSING
# ===============================
def preprocess_image_pytorch(image_file):
    try:
        image = Image.open(image_file).convert('RGB')
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        return transform(image).unsqueeze(0)
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        raise

# ===============================
# PREDICTION
# ===============================
def predict_with_model(model, image_tensor, classes):
    try:
        with torch.no_grad():
            outputs = model(image_tensor)
            probs = torch.softmax(outputs, dim=1).cpu().numpy()[0]
            class_idx = int(np.argmax(probs))
            confidence = float(probs[class_idx]) * 100
            predicted_class = classes[class_idx]
            return predicted_class, confidence
    except Exception as e:
        print(f"Prediction error: {e}")
        return "Unknown", 0.0

# ===============================
# CLASSES
# ===============================
DISEASE_CLASSES = [
    'Black Pod Rot',
    'Fito Disease',
    'Healthy',
    'Monilia Disease',
    'Unknown',
    'Mirids'
]

PEST_CLASSES = [
    'Ant Weaver',
    'Aphids',
    'Healthy',
    'Mealy Bug',
    'Unknown Data',
    'Cocoa Pod Borer'
]

# ===============================
# RECOMMENDATIONS
# ===============================
DISEASE_RECOMMENDATIONS = {
    'Black Pod Rot': [
        'Remove and destroy infected pods immediately',
        'Improve drainage and air circulation',
        'Apply copper-based fungicides',
        'Harvest ripe pods promptly'
    ],
    'Fito Disease': [
        'Remove affected pods and leaves',
        'Use resistant varieties when possible',
        'Apply appropriate fungicides during wet season'
    ],
    'Healthy': [
        'Plant is healthy. Maintain good farm practices.'
    ],
    'Monilia Disease': [
        'Prune and destroy infected plant parts',
        'Improve ventilation between trees',
        'Apply fungicides preventively'
    ],
    'Unknown': [
        'Unable to identify disease. Try scanning a clearer image.'
    ],
    'Mirids': [
        'Prune infested shoots',
        'Apply recommended insecticide',
        'Encourage natural predators',
        'Monitor regularly'
    ]
}

PEST_RECOMMENDATIONS = {
    'Ant Weaver': [
        'Destroy ant nests manually',
        'Apply safe insecticides around the base',
        'Encourage natural predators'
    ],
    'Aphids': [
        'Spray neem oil or insecticidal soap',
        'Introduce ladybugs as natural predators',
        'Avoid excessive nitrogen fertilization'
    ],
    'Healthy': [
        'Plant is healthy. Maintain good farm practices.'
    ],
    'Mealy Bug': [
        'Remove manually with alcohol swabs',
        'Apply systemic insecticides if infestation is severe'
    ],
    'Unknown Data': [
        'Unable to identify pest. Try scanning a clearer image.'
    ],
    'Cocoa Pod Borer': [
        'Harvest and destroy infested pods',
        'Use pheromone traps for monitoring',
        'Apply biological control agents'
    ]
}

# Combined recommendations dictionary for scan_history
RECOMMENDATIONS = {**DISEASE_RECOMMENDATIONS, **PEST_RECOMMENDATIONS}


# ===============================
# PREDICT IMAGE (Unified)
# ===============================
def predict_image(image_file, scan_type="disease"):
    image_tensor = preprocess_image_pytorch(image_file)

    if scan_type == 'disease' and disease_model:
        result, confidence = predict_with_model(disease_model, image_tensor, DISEASE_CLASSES)
        recommendations = DISEASE_RECOMMENDATIONS.get(result, ['No recommendation available'])
    elif scan_type == 'pest' and pest_model:
        result, confidence = predict_with_model(pest_model, image_tensor, PEST_CLASSES)
        recommendations = PEST_RECOMMENDATIONS.get(result, ['No recommendation available'])
    else:
        result, confidence = "Unknown", 0.0
        recommendations = ['No recommendation available']

    return result, confidence, recommendations

# ===============================
# SCAN VIEW
# ===============================
@csrf_exempt
def scan_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        scan_type = request.POST.get('scan_type', 'disease')

        result, confidence, recommendations = predict_image(image_file, scan_type)

        return JsonResponse({
            'success': True,
            'result': result,
            'confidence': round(confidence, 2),
            'recommendations': recommendations
        })

    return JsonResponse({'success': False, 'message': 'Invalid request'})


def scan_diagnose_view(request):
    return render(request, 'user/scan_diagnose.html')
def admin_user_management(request):
    return render(request, 'admin/user_management.html')

from torchvision import transforms
from PIL import Image

@csrf_exempt
def scan_image(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

    if 'image' not in request.FILES:
        return JsonResponse({'success': False, 'message': 'No image uploaded'})

    scan_type = request.POST.get('scan_type', 'disease')
    uploaded_file = request.FILES['image']

    # Save temporarily
    temp_path = os.path.join('temp_uploads', uploaded_file.name)
    path = default_storage.save(temp_path, ContentFile(uploaded_file.read()))
    full_path = os.path.join(settings.MEDIA_ROOT, path)

    try:
        if scan_type == 'disease' and disease_model:
            result, confidence = predict_image(full_path, disease_model, DISEASE_CLASSES)
            recommendations = DISEASE_RECOMMENDATIONS.get(result, ["No specific advice available."])
        elif scan_type == 'pest' and pest_model:
            result, confidence = predict_image(full_path, pest_model, PEST_CLASSES)
            recommendations = PEST_RECOMMENDATIONS.get(result, ["No specific advice available."])
        else:
            return JsonResponse({'success': False, 'message': 'Model not available for this scan type'})

        # Build scan data
        scan_data = {
            'scan_id': str(datetime.now(pytz.timezone('Asia/Manila')).timestamp()),
            'type': scan_type,
            'result': result,
            'confidence': confidence,
            'recommendations': recommendations,
            'timestamp': datetime.now(pytz.timezone('Asia/Manila')).isoformat(),
            'image_path': f"scans/{uploaded_file.name}"
        }

        # Clean up
        default_storage.delete(path)

        return JsonResponse({'success': True, 'scan_data': scan_data})

    except Exception as e:
        if os.path.exists(full_path):
            default_storage.delete(path)
        return JsonResponse({'success': False, 'message': f'Error processing image: {str(e)}'})


def scan_history(request):
    # Generate realistic dummy history with 10 items (5 disease, 5 pest)
    now = datetime.now(pytz.timezone('Asia/Manila'))
    history = []
    
    # Disease scans
    disease_results = ['Black Pod Disease', 'Fito Disease', 'Monilia Disease', 'Frosty Pod Rot', 'Witches Broom', 'Healthy', 'Unknown']
    for i in range(5):
        result = disease_results[i]
        history.append({
            'scan_id': f'd{i+1}',
            'type': 'disease',
            'result': result,
            'confidence': round(85 + i*3 + (5 if result == 'Healthy' else 0)),  # Fixed missing parenthesis
            'recommendations': RECOMMENDATIONS.get(result, RECOMMENDATIONS['Healthy']),
            'timestamp': (now - timedelta(days=i+1)).isoformat(),
            'image_path': f'scans/disease_{i+1}.jpg'
        })
    
    # Pest scans
    pest_results = ['Cocoa Pod Borer', 'Ant Weaver', 'Mealybugs', 'Aphids', 'Healthy', 'Unknown']
    for i in range(5):
        result = pest_results[i]
        history.append({
            'scan_id': f'p{i+1}',
            'type': 'pest',
            'result': result,
            'confidence': round(80 + i*4 + (8 if result == 'Healthy' else 0)),  # Healthy gets higher confidence
            'recommendations': RECOMMENDATIONS.get(result, RECOMMENDATIONS['Healthy']),
            'timestamp': (now - timedelta(days=i+6)).isoformat(),
            'image_path': f'scans/pest_{i+1}.jpg'
        })
    
    
    # Sort by timestamp (newest first)
    history.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return JsonResponse({
        'success': True,
        'scans': history
    })

@csrf_exempt
def delete_scan(request, scan_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid method'})
    
    # In a real app, implement actual deletion logic here
    return JsonResponse({
        'status': 'success',
        'message': f'Scan {scan_id} deleted successfully'
    })



from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta
import json
from firebase_admin import firestore


@csrf_exempt
def dashboard_data_api(request):
    """API endpoint for real-time dashboard updates"""
    if request.method == 'GET':
        try:
            # Get quick counts
            users_count = len(list(db.collection('users').stream()))
            scans_count = len(list(db.collection('scans').stream()))
            orders_count = len(list(db.collection('orders').stream()))
            
            # Calculate revenue
            orders_ref = db.collection('orders')
            delivered_orders = orders_ref.where('status', '==', 'delivered').stream()
            revenue = sum(float(o.to_dict().get('total_amount', 0)) for o in delivered_orders)
            
            return JsonResponse({
                'success': True,
                'data': {
                    'total_users': users_count,
                    'total_scans': scans_count,
                    'total_orders': orders_count,
                    'total_revenue': revenue,
                    'timestamp': timezone.now().isoformat()
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})





from datetime import datetime, timedelta
from django.shortcuts import render
from firebase_admin import firestore
import json

@admin_required
def admin_dashboard(request):
    """Admin dashboard with real data counting from Firestore"""
    db = firestore.client()
    
    # Get current date and calculate date ranges
    today = datetime.now(pytz.timezone('Asia/Manila'))
    current_date = today.date()
    last_30_days = today - timedelta(days=30)
    
    # Initialize counts
    counts = {
        'user_count': 0,
        'order_count': 0,
        'total_revenue': 0,
        'farm_count': 0,
    }
    
    # Initialize recent activity lists
    recent_activity = {
        'recent_users': [],
        'recent_orders': [],
        'recent_scans': [],
    }
    
    # Initialize chart data
    chart_data = {
        'user_growth_labels': [],
        'user_growth_data': [],
        'revenue_labels': [],
        'revenue_data': [],
    }
    
    try:
        # Count total users
        users_ref = db.collection('users')
        counts['user_count'] = len(list(users_ref.stream()))
        
        # Get recent users (last 5)
        recent_users_query = users_ref.order_by('created_at', direction=firestore.Query.DESCENDING).limit(5)
        for doc in recent_users_query.stream():
            user_data = doc.to_dict()
            recent_activity['recent_users'].append({
                'name': user_data.get('name', 'Unknown'),
                'email': user_data.get('email', 'No email'),
                'created_at': user_data.get('created_at', '').strftime('%b %d') if hasattr(user_data.get('created_at', ''), 'strftime') else ''
            })
        
        # Count orders and calculate revenue
        orders_ref = db.collection('orders')
        counts['order_count'] = len(list(orders_ref.stream()))
        
        # Calculate total revenue from delivered orders
        delivered_orders = orders_ref.where('status', '==', 'delivered').stream()
        counts['total_revenue'] = sum(float(order.to_dict().get('total_amount', 0)) for order in delivered_orders)
        
        # Get recent orders (last 5)
        recent_orders_query = orders_ref.order_by('created_at', direction=firestore.Query.DESCENDING).limit(5)
        for doc in recent_orders_query.stream():
            order_data = doc.to_dict()
            recent_activity['recent_orders'].append({
                'id': doc.id,
                'amount': order_data.get('total_amount', 0),
                'status': order_data.get('status', 'pending'),
                'created_at': order_data.get('created_at', '').strftime('%b %d') if hasattr(order_data.get('created_at', ''), 'strftime') else ''
            })
        
        # Count total farms (combining Firestore and sample data)
        farms_ref = db.collection('farms')
        counts['farm_count'] = len(list(farms_ref.stream())) + len(SAMPLE_FARMS)
        
        # Get recent scans (last 5)
        scans_ref = db.collection('scans')
        recent_scans_query = scans_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(5)
        for doc in recent_scans_query.stream():
            scan_data = doc.to_dict()
            recent_activity['recent_scans'].append({
                'type': scan_data.get('type', 'disease'),
                'result': scan_data.get('result', 'Unknown'),
                'confidence': scan_data.get('confidence', 0),
                'date': scan_data.get('timestamp', '').strftime('%b %d') if hasattr(scan_data.get('timestamp', ''), 'strftime') else ''
            })
        
        # Generate user growth data (last 30 days)
        user_growth = {}
        for i in range(30):
            date = (today - timedelta(days=i)).date()
            user_growth[date.strftime('%b %d')] = 0
        
        users = users_ref.where('created_at', '>=', last_30_days).stream()
        for user in users:
            user_data = user.to_dict()
            if 'created_at' in user_data and hasattr(user_data['created_at'], 'date'):
                date_key = user_data['created_at'].date().strftime('%b %d')
                user_growth[date_key] = user_growth.get(date_key, 0) + 1
        
        chart_data['user_growth_labels'] = list(user_growth.keys())[::-1]
        chart_data['user_growth_data'] = list(user_growth.values())[::-1]
        
        # Generate revenue data (last 30 days)
        revenue_data = {}
        for i in range(30):
            date = (today - timedelta(days=i)).date()
            revenue_data[date.strftime('%b %d')] = 0
        
        orders = orders_ref.where('status', '==', 'delivered').where('created_at', '>=', last_30_days).stream()
        for order in orders:
            order_data = order.to_dict()
            if 'created_at' in order_data and hasattr(order_data['created_at'], 'date'):
                date_key = order_data['created_at'].date().strftime('%b %d')
                revenue_data[date_key] = revenue_data.get(date_key, 0) + float(order_data.get('total_amount', 0))
        
        chart_data['revenue_labels'] = list(revenue_data.keys())[::-1]
        chart_data['revenue_data'] = list(revenue_data.values())[::-1]
        
    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
    
    # Prepare context with all data
    context = {
        'current_date': current_date,
        'user_count': counts['user_count'],
        'order_count': counts['order_count'],
        'total_revenue': counts['total_revenue'],
        'farm_count': counts['farm_count'],
        'recent_users': recent_activity['recent_users'],
        'recent_orders': recent_activity['recent_orders'],
        'recent_scans': recent_activity['recent_scans'],
        'user_growth_labels': json.dumps(chart_data['user_growth_labels']),
        'user_growth_data': json.dumps(chart_data['user_growth_data']),
        'revenue_labels': json.dumps(chart_data['revenue_labels']),
        'revenue_data': json.dumps(chart_data['revenue_data']),
    }
    
    return render(request, 'admin/admin_dashboard.html', context)


#Account
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .decorators import user_required, admin_required
from .firebase_utils import (
    get_user_profile, save_user_profile, get_all_users, 
    delete_firebase_user, set_user_role, upload_profile_image,
    delete_profile_image, get_user_role)
from firebase_admin import auth

# User Profile Views
@user_required
def profile_view(request):
    # Try multiple possible session keys
    uid = (request.session.get('firebase_uid') or 
           request.session.get('uid') or 
           request.session.get('user_id'))
    
    if not uid:
        messages.error(request, "Session expired. Please log in again.")
        return redirect('login')

    profile = get_user_profile(uid)
    try:
        user = auth.get_user(uid)
        user_email = user.email
        user_name = user.display_name or ''
    except:
        user_email = ''
        user_name = ''

    if not profile:
        profile = {
            'full_name': user_name,
            'email': user_email,
            'phone_number': '',
            'location': '',
            'bio': '',
            'profile_image': None
        }

    context = {
        'profile': profile,
        'user_email': user_email,
        'default_avatar': '/static/img/default-avatar.jpg'
    }
    return render(request, 'user/profile.html', context)

@user_required
def profile_edit(request):
    # Try multiple possible session keys
    uid = (request.session.get('firebase_uid') or 
           request.session.get('uid') or 
           request.session.get('user_id'))
    
    if not uid:
        messages.error(request, "Session expired. Please log in again.")
        return redirect('login')

    if request.method == 'POST':
        try:
            full_name = request.POST.get('full_name', '').strip()
            phone_number = request.POST.get('phone_number', '').strip()
            location = request.POST.get('location', '').strip()
            bio = request.POST.get('bio', '').strip()
            email = request.POST.get('email', '').strip()  # Get email from form

            # Validation
            if not full_name:
                messages.error(request, 'Full name is required.')
                return redirect('profile_view')

            if len(full_name) > 100:
                messages.error(request, 'Full name must be less than 100 characters.')
                return redirect('profile_view')

            if phone_number and len(phone_number) > 20:
                messages.error(request, 'Phone number must be less than 20 characters.')
                return redirect('profile_view')

            if len(bio) > 500:
                messages.error(request, 'Bio must be less than 500 characters.')
                return redirect('profile_view')

            # Get existing profile
            profile = get_user_profile(uid) or {}

            # Update profile data including email
            profile.update({
                'full_name': full_name,
                'email': email,  # Include email in profile
                'phone_number': phone_number,
                'location': location,
                'bio': bio
            })

            # Handle profile image upload
            if 'profile_image' in request.FILES:
                image_file = request.FILES['profile_image']
                
                # Validate file size (5MB)
                if image_file.size > 5 * 1024 * 1024:
                    messages.error(request, 'Image file size must be less than 5MB.')
                    return redirect('profile_view')

                # Validate file type
                allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
                if image_file.content_type not in allowed_types:
                    messages.error(request, 'Only JPG, PNG, GIF, and WebP images are allowed.')
                    return redirect('profile_view')

                # Delete old image if exists
                if profile.get('profile_image'):
                    delete_profile_image(profile['profile_image'])

                # Upload new image
                image_url = upload_profile_image(uid, image_file)
                if image_url:
                    profile['profile_image'] = image_url
                else:
                    messages.error(request, 'Failed to upload image.')
                    return redirect('profile_view')

            # Save profile
            if save_user_profile(uid, profile):
                messages.success(request, 'Profile updated successfully!')
            else:
                messages.error(request, 'Failed to update profile.')

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')

    return redirect('profile_view')

# Only replace the image upload functions

@user_required
@csrf_exempt
@require_http_methods(["POST"])
def profile_image_upload_ajax(request):
    """Handle AJAX profile image upload to Firestore"""
    uid = (request.session.get('firebase_uid') or 
           request.session.get('uid') or 
           request.session.get('user_id'))
    
    if not uid:
        return JsonResponse({'success': False, 'message': 'Session expired'})

    try:
        if 'profile_image' in request.FILES:
            image_file = request.FILES['profile_image']
            
            # Validate file size (1MB limit for Firestore - base64 increases size by ~33%)
            max_size = 1 * 1024 * 1024  # 1MB
            if image_file.size > max_size:
                return JsonResponse({
                    'success': False, 
                    'message': 'Image file size must be less than 1MB for Firestore storage.'
                })

            # Validate file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if image_file.content_type not in allowed_types:
                return JsonResponse({
                    'success': False, 
                    'message': 'Only JPG, PNG, GIF, and WebP images are allowed.'
                })

            # Reset file pointer to beginning
            image_file.seek(0)

            # Get existing profile
            profile = get_user_profile(uid) or {}

            # Upload new image (store as base64 in Firestore)
            image_data_url = upload_profile_image(uid, image_file)
            if image_data_url:
                profile['profile_image'] = image_data_url
                if save_user_profile(uid, profile):
                    return JsonResponse({
                        'success': True,
                        'message': 'Profile image updated successfully!',
                        'image_url': image_data_url
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Failed to save profile data.'
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Failed to upload image to Firestore.'
                })
        else:
            return JsonResponse({
                'success': False,
                'message': 'No image file provided.'
            })
            
    except Exception as e:
        print(f"Error in profile_image_upload_ajax: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error uploading image: {str(e)}'
        })

@user_required
@csrf_exempt
@require_http_methods(["POST"])
def delete_profile_image_view(request):
    """Handle profile image deletion from Firestore"""
    uid = (request.session.get('firebase_uid') or 
           request.session.get('uid') or 
           request.session.get('user_id'))
    
    if not uid:
        return JsonResponse({'success': False, 'message': 'Session expired'})

    try:
        profile = get_user_profile(uid)
        if profile and profile.get('profile_image'):
            # Remove image from profile
            profile['profile_image'] = None
            profile['profile_image_mime_type'] = None
            profile['profile_image_size'] = None
            
            if save_user_profile(uid, profile):
                return JsonResponse({
                    'success': True, 
                    'message': 'Profile image deleted successfully!'
                })
            else:
                return JsonResponse({
                    'success': False, 
                    'message': 'Failed to update profile.'
                })
        else:
            return JsonResponse({
                'success': False, 
                'message': 'No image to delete.'
            })
    except Exception as e:
        print(f"Error deleting profile image: {e}")
        return JsonResponse({
            'success': False, 
            'message': f'Error deleting image: {str(e)}'
        })

#Accounts End Good

#admin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import UserCreationForm
from django import forms
import json

User = get_user_model()

# Custom User Creation Form
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

# Custom User Edit Form
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

from django.shortcuts import render
from firebase_admin import firestore

def admin_user_list(request):
    db = firestore.client()
    users_ref = db.collection('users')
    docs = users_ref.stream()

    users = []
    for doc in docs:
        data = doc.to_dict()
        users.append({
            'email': data.get('email'),
            'role': data.get('role', 'user'),
            'is_active': data.get('is_active', True),
            'date_joined': data.get('created_at'),
            'profile': {
                'full_name': data.get('full_name', ''),
                'profile_image': data.get('profile_image', None)
            },
            'username': data.get('display_name', '').replace(' ', '').lower()
        })

    context = {
        'users': users,
        'total_users': len(users),
        'active_users': len([u for u in users if u['is_active']]),
        'inactive_users': len([u for u in users if not u['is_active']]),
        'admin_users': len([u for u in users if u['role'] == 'admin']),
    }

    return render(request, 'admin/user_list.html', context)



from django.shortcuts import render, redirect
from django.contrib import messages
from firebase_admin import auth as firebase_auth, firestore


@admin_required
def user_create(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        display_name = request.POST.get('display_name')
        full_name = request.POST.get('full_name', '')
        phone_number = request.POST.get('phone_number', '')
        location = request.POST.get('location', '')
        role = request.POST.get('role', 'user')
        bio = request.POST.get('bio', '')

        if not email or not display_name:
            messages.error(request, 'Email and Display Name are required.')
        else:
            try:
                # Create user in Firebase Auth
                user = firebase_auth.create_user(
                    email=email,
                    display_name=display_name,
                    phone_number=phone_number if phone_number else None
                )

                # Optional: Set custom claims (e.g., role)
                firebase_auth.set_custom_user_claims(user.uid, {'role': role})

                # Save additional user details in Firestore
                db = firestore.client()
                db.collection('users').document(user.uid).set({
                    'uid': user.uid,
                    'email': email,
                    'display_name': display_name,
                    'full_name': full_name,
                    'phone_number': phone_number,
                    'location': location,
                    'role': role,
                    'bio': bio,
                    'created_at': firestore.SERVER_TIMESTAMP,
                })

                messages.success(request, f'User "{display_name}" created successfully!')
                return redirect('admin_user_list')
            except Exception as e:
                messages.error(request, f'Error creating user: {str(e)}')

    return render(request, 'admin/user_form.html', {
        'title': 'Create New User',
        'submit_text': 'Create User',
    })

#end user

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages

from .decorators import admin_required
import json
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore
import pytz
import random

# Initialize Firestore

# Sample farm data (fallback)
SAMPLE_FARMS = [
    {
        'id': 1,
        'name': 'Barangay Poblacion Farm',
        'municipality': 'Victoria',
        'barangay': 'Poblacion',
        'area': 4.5,
        'trees': 10,
        'status': 'Active',
        'lat': 13.1375,
        'lng': 121.2410,
        'description': 'Primary cacao growing area with established farms',
        'contact': 'Brgy. Captain Juan Santos',
        'created_at': '2024-01-15',
        'images': [
            '/static/images/download (2).jpg',
            '/static/images/download (1).jpg',
            '/static/images/download (3).jpg'
        ]

    },
    {
        'id': 2,
        'name': 'San Vicente Cacao Farm',
        'municipality': 'Victoria',
        'barangay': 'San Vicente',
        'area': 3.2,
        'trees': 15,
        'status': 'Active',
        'lat': 13.1500,
        'lng': 121.2333,
        'description': 'Emerging farming community with modern techniques',
        'contact': 'Brgy. Captain Maria Cruz',
        'created_at': '2024-01-14',
        'images': [
            '/static/images/download (1).jpg',
            '/static/images/download.jpg'
        ]
    },
    {
        'id': 3,
        'name': 'Macatoc Cacao Farm',
        'municipality': 'Victoria',
        'barangay': 'Macatoc',
        'area': 8.5,
        'trees': 13,
        'status': 'Monitoring',
        'lat': 13.1440,
        'lng': 121.2320,
        'description': 'Large scale cacao production facility',
        'contact': 'Farm Manager Pedro Reyes',
        'created_at': '2024-01-13',
        'images': [
            '/static/images/download (3).jpg',
            '/static/images/download (2).jpg'
        ]
    }
]

@admin_required
def admin_dashboard(request):
    """Enhanced Admin Dashboard with comprehensive analytics"""
    print("[DEBUG] Accessing Admin Dashboard:", request.session.get('user_email'), request.session.get('role'))
    
    # Initialize timezone
    tz = pytz.timezone('Asia/Manila')
    today = datetime.now(tz)
    
    # Initialize default values
    context = {
        'name': request.session.get('name'),
        'email': request.session.get('user_email'),
        'role': request.session.get('role'),
        'current_date': today.strftime('%Y-%m-%d'),
        'current_time': today.strftime('%H:%M:%S'),
        
        # Default values
        'total_scan_count': 0,
        'order_count': 0,
        'total_revenue': 0,
        'farm_count': len(SAMPLE_FARMS),
        
        # Recent activity
        'recent_farms': SAMPLE_FARMS[:3],
        'recent_orders': [],
        'recent_scans': [],
        
        # Chart data (initialize as empty)
        'revenue_labels': json.dumps([]),
        'revenue_data': json.dumps([]),
        'scan_labels': json.dumps([]),
        'scan_data': json.dumps([]),
    }
    
    try:
        # ===== FETCH SCANS DATA =====
        print("[DEBUG] Fetching scans data...")
        scans_ref = db.collection('scans')
        all_scans = list(scans_ref.stream())
        total_scan_count = len(all_scans)
        
        print(f"[DEBUG] Found {total_scan_count} total scans")
        
        # Get recent scans for activity
        recent_scans = []
        scans_by_date = sorted(all_scans, key=lambda x: x.to_dict().get('timestamp', datetime.now(pytz.timezone('Asia/Manila'))), reverse=True)
        
        for doc in scans_by_date[:5]:
            scan_data = doc.to_dict()
            timestamp = scan_data.get('timestamp')
            if timestamp:
                if hasattr(timestamp, 'seconds'):
                    formatted_date = datetime.fromtimestamp(timestamp.seconds).strftime('%b %d')
                else:
                    formatted_date = timestamp.strftime('%b %d') if hasattr(timestamp, 'strftime') else 'Recent'
            else:
                formatted_date = 'Recent'
                
            recent_scans.append({
                'result': scan_data.get('result', 'Unknown'),
                'confidence': round(float(scan_data.get('confidence', 0))),
                'type': scan_data.get('type', 'disease'),
                'date': formatted_date
            })
        
        # Prepare scan chart data (last 7 days)
        scan_labels = []
        scan_counts = []
        
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime('%b %d')
            scan_labels.append(date_str)
            
            # Count scans for this date
            daily_scans = 0
            for scan_doc in all_scans:
                scan_data = scan_doc.to_dict()
                scan_timestamp = scan_data.get('timestamp')
                if scan_timestamp:
                    if hasattr(scan_timestamp, 'seconds'):
                        scan_date = datetime.fromtimestamp(scan_timestamp.seconds).date()
                    else:
                        scan_date = scan_timestamp.date() if hasattr(scan_timestamp, 'date') else today.date()
                    
                    if scan_date == date.date():
                        daily_scans += 1
            
            scan_counts.append(daily_scans)
        
        context.update({
            'total_scan_count': total_scan_count,
            'recent_scans': recent_scans,
            'scan_labels': json.dumps(scan_labels),
            'scan_data': json.dumps(scan_counts),
        })
        
    except Exception as e:
        print(f"[ERROR] Error fetching scans data: {e}")
        # Use fallback data for scans
        context.update({
            'total_scan_count': 45,  # Fallback number
            'recent_scans': [
                {'result': 'Healthy', 'confidence': 95, 'type': 'disease', 'date': 'Jan 15'},
                {'result': 'Black Pod Disease', 'confidence': 87, 'type': 'disease', 'date': 'Jan 14'},
                {'result': 'Monilia Disease', 'confidence': 92, 'type': 'pest', 'date': 'Jan 13'},
                {'result': 'Healthy', 'confidence': 89, 'type': 'pest', 'date': 'Jan 12'},
                {'result': 'Frosty Pod Rot', 'confidence': 84, 'type': 'disease', 'date': 'Jan 11'},
            ],
            'scan_labels': json.dumps(['Jan 09', 'Jan 10', 'Jan 11', 'Jan 12', 'Jan 13', 'Jan 14', 'Jan 15']),
            'scan_data': json.dumps([3, 5, 8, 6, 9, 7, 12]),
        })
    
    try:
        # ===== FETCH ORDERS DATA =====
        print("[DEBUG] Fetching orders data...")
        orders_ref = db.collection('orders')
        all_orders = list(orders_ref.stream())
        order_count = len(all_orders)
        
        # Calculate total revenue from delivered orders
        total_revenue = 0
        recent_orders = []
        
        orders_by_date = sorted(all_orders, key=lambda x: x.to_dict().get('created_at', datetime.now(pytz.timezone('Asia/Manila'))), reverse=True)
        
        for doc in orders_by_date:
            order_data = doc.to_dict()
            
            # Add to revenue if delivered
            if order_data.get('status') == 'delivered':
                total_revenue += float(order_data.get('total_amount', 0))
            
            # Add to recent orders (first 5)
            if len(recent_orders) < 5:
                created_at = order_data.get('created_at')
                if created_at:
                    if hasattr(created_at, 'seconds'):
                        formatted_date = datetime.fromtimestamp(created_at.seconds).strftime('%b %d')
                    else:
                        formatted_date = created_at.strftime('%b %d') if hasattr(created_at, 'strftime') else 'Recent'
                else:
                    formatted_date = 'Recent'
                
                recent_orders.append({
                    'id': doc.id,
                    'amount': float(order_data.get('total_amount', 0)),
                    'status': order_data.get('status', 'pending'),
                    'created_at': formatted_date
                })
        
        # Prepare revenue chart data (last 7 days)
        revenue_labels = []
        revenue_data = []
        
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime('%b %d')
            revenue_labels.append(date_str)
            
            # Calculate revenue for this date
            daily_revenue = 0
            for order_doc in all_orders:
                order_data = order_doc.to_dict()
                if order_data.get('status') == 'delivered':
                    order_timestamp = order_data.get('created_at')
                    if order_timestamp:
                        if hasattr(order_timestamp, 'seconds'):
                            order_date = datetime.fromtimestamp(order_timestamp.seconds).date()
                        else:
                            order_date = order_timestamp.date() if hasattr(order_timestamp, 'date') else today.date()
                        
                        if order_date == date.date():
                            daily_revenue += float(order_data.get('total_amount', 0))
            
            revenue_data.append(daily_revenue)
        
        context.update({
            'order_count': order_count,
            'total_revenue': round(total_revenue, 2),
            'recent_orders': recent_orders,
            'revenue_labels': json.dumps(revenue_labels),
            'revenue_data': json.dumps(revenue_data),
        })
        
    except Exception as e:
        print(f"[ERROR] Error fetching orders data: {e}")
        # Use fallback data for orders
        context.update({
            'order_count': 28,
            'total_revenue': 15750.00,
            'recent_orders': [
                {'id': 'ORD001', 'amount': 1250.00, 'status': 'delivered', 'created_at': 'Jan 15'},
                {'id': 'ORD002', 'amount': 890.00, 'status': 'pending', 'created_at': 'Jan 14'},
                {'id': 'ORD003', 'amount': 2100.00, 'status': 'delivered', 'created_at': 'Jan 13'},
                {'id': 'ORD004', 'amount': 675.00, 'status': 'shipped', 'created_at': 'Jan 12'},
                {'id': 'ORD005', 'amount': 1450.00, 'status': 'delivered', 'created_at': 'Jan 11'},
            ],
            'revenue_labels': json.dumps(['Jan 09', 'Jan 10', 'Jan 11', 'Jan 12', 'Jan 13', 'Jan 14', 'Jan 15']),
            'revenue_data': json.dumps([1200, 2100, 1800, 2400, 1950, 2800, 3200]),
        })
    
    try:
        # ===== FETCH FARMS DATA =====
        print("[DEBUG] Fetching farms data...")
        farms_ref = db.collection('farms')
        firebase_farms = list(farms_ref.stream())
        
        # Combine Firebase farms with sample farms
        total_farm_count = len(SAMPLE_FARMS) + len(firebase_farms)
        
        # Prepare recent farms (prioritize sample farms for display)
        recent_farms = SAMPLE_FARMS[:3]  # Show first 3 sample farms
        
        context.update({
            'farm_count': total_farm_count,
            'recent_farms': recent_farms,
        })
        
    except Exception as e:
        print(f"[ERROR] Error fetching farms data: {e}")
        # Use sample farms as fallback
        context.update({
            'farm_count': len(SAMPLE_FARMS),
            'recent_farms': SAMPLE_FARMS[:3],
        })
    
    print(f"[DEBUG] Final context data:")
    print(f"  - Total Scans: {context['total_scan_count']}")
    print(f"  - Total Orders: {context['order_count']}")
    print(f"  - Total Revenue: {context['total_revenue']}")
    print(f"  - Total Farms: {context['farm_count']}")
    
    return render(request, 'admin/admin_dashboard.html', context)

@admin_required
def image_analysis(request):
    """Image Analysis view with scan data and charts"""
    print("[DEBUG] Accessing Image Analysis:", request.session.get('user_email'))
    
    # Initialize timezone
    tz = pytz.timezone('Asia/Manila')
    today = datetime.now(tz)
    
    # Initialize default values
    context = {
        'total_scans': 0,
        'disease_scans': 0,
        'pest_scans': 0,
        'today_scans': 0,
        'scans': [],
        'chart_data': json.dumps([]),
    }
    
    try:
        # ===== FETCH ALL USER SCANS DATA =====
        print("[DEBUG] Fetching user scans data...")
        
        # Try different collection names that might be used for user scans
        possible_collections = ['user_scans', 'scans', 'scan_results', 'image_scans']
        all_scans = []
        
        for collection_name in possible_collections:
            try:
                scans_ref = db.collection(collection_name)
                collection_scans = list(scans_ref.stream())
                if collection_scans:
                    print(f"[DEBUG] Found {len(collection_scans)} scans in collection '{collection_name}'")
                    all_scans.extend(collection_scans)
                    break  # Use the first collection that has data
            except Exception as e:
                print(f"[DEBUG] Collection '{collection_name}' not found or error: {e}")
                continue
        
        if not all_scans:
            print("[DEBUG] No scans found in any collection, trying to fetch from 'scans' with different structure")
            # Try fetching with different query structure
            try:
                scans_ref = db.collection('scans')
                all_scans = list(scans_ref.stream())
                print(f"[DEBUG] Found {len(all_scans)} scans in 'scans' collection")
            except Exception as e:
                print(f"[DEBUG] Error fetching from 'scans' collection: {e}")
        
        # Process scans data
        scans_list = []
        disease_count = 0
        pest_count = 0
        today_count = 0
        
        # Chart data for last 7 days
        chart_data = []
        daily_counts = {}
        
        # Initialize daily counts
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime('%b %d')
            daily_counts[date.strftime('%Y-%m-%d')] = 0
        
        print(f"[DEBUG] Processing {len(all_scans)} scans...")
        
        for scan_doc in all_scans:
            try:
                scan_data = scan_doc.to_dict()
                print(f"[DEBUG] Processing scan {scan_doc.id}: {scan_data}")
                
                # Handle different timestamp field names
                timestamp_field = None
                for field in ['timestamp', 'created_at', 'scan_date', 'date']:
                    if field in scan_data:
                        timestamp_field = field
                        break
                
                scan_timestamp = scan_data.get(timestamp_field) if timestamp_field else None
                
                # Format timestamp
                if scan_timestamp:
                    if hasattr(scan_timestamp, 'seconds'):
                        formatted_timestamp = datetime.fromtimestamp(scan_timestamp.seconds, tz)
                    elif isinstance(scan_timestamp, str):
                        try:
                            formatted_timestamp = datetime.fromisoformat(scan_timestamp.replace('Z', '+00:00'))
                            formatted_timestamp = formatted_timestamp.astimezone(tz)
                        except:
                            formatted_timestamp = today
                    else:
                        formatted_timestamp = scan_timestamp if hasattr(scan_timestamp, 'strftime') else today
                else:
                    formatted_timestamp = today
                
                # Handle different field names for scan type
                scan_type = scan_data.get('scan_type') or scan_data.get('type') or 'disease'
                
                # Handle different field names for result
                result = (scan_data.get('result') or 
                         scan_data.get('prediction') or 
                         scan_data.get('primary_class') or 
                         'Unknown')
                
                # Handle different field names for confidence
                confidence_raw = (scan_data.get('confidence') or 
                                scan_data.get('primary_confidence') or 
                                scan_data.get('score') or 0)
                
                # Convert confidence to percentage if needed
                if isinstance(confidence_raw, (int, float)):
                    if confidence_raw <= 1.0:
                        confidence = float(confidence_raw) * 100
                    else:
                        confidence = float(confidence_raw)
                else:
                    confidence = 0
                
                # Handle different field names for user info
                username = (scan_data.get('user_email') or 
                           scan_data.get('username') or 
                           scan_data.get('user') or 
                           'Unknown User')
                
                # Handle image name
                image_name = (scan_data.get('image_name') or 
                             scan_data.get('filename') or 
                             f'scan_{scan_doc.id[:8]}')
                
                # Count by type
                if scan_type == 'disease':
                    disease_count += 1
                elif scan_type == 'pest':
                    pest_count += 1
                
                # Count today's scans
                if formatted_timestamp.date() == today.date():
                    today_count += 1
                
                # Count for chart data
                scan_date_str = formatted_timestamp.strftime('%Y-%m-%d')
                if scan_date_str in daily_counts:
                    daily_counts[scan_date_str] += 1
                
                # Add to scans list
                scans_list.append({
                    'id': scan_doc.id,
                    'type': scan_type,
                    'primary_class': result,
                    'primary_confidence': confidence,
                    'image_name': image_name,
                    'username': username,
                    'timestamp': formatted_timestamp,
                    'hidden': scan_data.get('hidden', False),
                    'raw_data': scan_data  # Keep raw data for debugging
                })
                
            except Exception as e:
                print(f"[ERROR] Error processing scan {scan_doc.id}: {e}")
                continue
        
        # Prepare chart data
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime('%b %d')
            date_key = date.strftime('%Y-%m-%d')
            chart_data.append({
                'date': date_str,
                'count': daily_counts.get(date_key, 0)
            })
        
        # Sort scans by timestamp (newest first)
        scans_list.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Filter out hidden scans unless specifically requested
        if request.GET.get('show_hidden') != 'true':
            visible_scans = [scan for scan in scans_list if not scan.get('hidden', False)]
        else:
            visible_scans = scans_list
        
        context.update({
            'total_scans': len(scans_list),
            'disease_scans': disease_count,
            'pest_scans': pest_count,
            'today_scans': today_count,
            'scans': visible_scans,
            'chart_data': json.dumps(chart_data),
        })
        
        print(f"[DEBUG] Final counts - Total: {len(scans_list)}, Disease: {disease_count}, Pest: {pest_count}, Today: {today_count}")
        
    except Exception as e:
        print(f"[ERROR] Error fetching scans data: {e}")
        import traceback
        traceback.print_exc()
        
        # Use fallback data
        fallback_chart_data = []
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            fallback_chart_data.append({
                'date': date.strftime('%b %d'),
                'count': random.randint(2, 15)
            })
        
        context.update({
            'total_scans': 42,
            'disease_scans': 28,
            'pest_scans': 14,
            'today_scans': 5,
            'scans': [
                {
                    'id': 'sample1',
                    'type': 'disease',
                    'primary_class': 'Black Pod Disease',
                    'primary_confidence': 87.5,
                    'image_name': 'cacao_leaf_001.jpg',
                    'username': 'farmer@example.com',
                    'timestamp': today,
                    'hidden': False
                },
                {
                    'id': 'sample2',
                    'type': 'pest',
                    'primary_class': 'Monilia',
                    'primary_confidence': 92.3,
                    'image_name': 'cacao_pod_002.jpg',
                    'username': 'user@example.com',
                    'timestamp': today - timedelta(hours=2),
                    'hidden': False
                }
            ],
            'chart_data': json.dumps(fallback_chart_data),
        })
    
    return render(request, 'admin/image_analysis.html', context)

@admin_required
def debug_firestore_collections(request):
    """Debug endpoint to see what collections and data exist in Firestore"""
    if not request.user.is_superuser and request.session.get('role') != 'Admin':
        return JsonResponse({'error': 'Access denied'})
    
    try:
        # List all collections
        collections = db.collections()
        collection_info = {}
        
        for collection in collections:
            collection_name = collection.id
            try:
                docs = list(collection.limit(5).stream())  # Get first 5 docs
                collection_info[collection_name] = {
                    'count': len(list(collection.stream())),
                    'sample_docs': []
                }
                
                for doc in docs:
                    doc_data = doc.to_dict()
                    collection_info[collection_name]['sample_docs'].append({
                        'id': doc.id,
                        'fields': list(doc_data.keys()),
                        'sample_data': {k: str(v)[:100] for k, v in doc_data.items()}  # Truncate long values
                    })
            except Exception as e:
                collection_info[collection_name] = {'error': str(e)}
        
        return JsonResponse({
            'success': True,
            'collections': collection_info
        }, indent=2)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@admin_required
@csrf_exempt
def toggle_scan_visibility(request, scan_id):
    """Toggle scan visibility (hide/unhide)"""
    if request.method == 'POST':
        try:
            scan_ref = db.collection('scans').document(scan_id)
            scan_doc = scan_ref.get()
            
            if scan_doc.exists:
                current_hidden = scan_doc.to_dict().get('hidden', False)
                scan_ref.update({'hidden': not current_hidden})
                
                action = 'hidden' if not current_hidden else 'shown'
                return JsonResponse({
                    'success': True,
                    'message': f'Scan {action} successfully',
                    'hidden': not current_hidden
                })
            else:
                return JsonResponse({'success': False, 'message': 'Scan not found'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@admin_required
@csrf_exempt
def delete_scan(request, scan_id):
    """Delete a scan"""
    if request.method == 'POST':
        try:
            scan_ref = db.collection('scans').document(scan_id)
            scan_ref.delete()
            messages.success(request, 'Scan deleted successfully')
        except Exception as e:
            messages.error(request, f'Error deleting scan: {str(e)}')
    
    return redirect('image_analysis')

@admin_required
def export_scan_data(request):
    """Export scan data as CSV"""
    import csv
    from django.http import HttpResponse
    
    try:
        # Fetch all scans
        scans_ref = db.collection('scans')
        all_scans = list(scans_ref.stream())
        
        # Create HTTP response with CSV content type
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="scan_data_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Scan ID', 'Type', 'Result', 'Confidence (%)', 'User Email', 'Image Name', 'Timestamp', 'Hidden'])
        
        for scan_doc in all_scans:
            scan_data = scan_doc.to_dict()
            timestamp = scan_data.get('timestamp')
            
            if timestamp:
                if hasattr(timestamp, 'seconds'):
                    formatted_timestamp = datetime.fromtimestamp(timestamp.seconds).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S') if hasattr(timestamp, 'strftime') else 'Unknown'
            else:
                formatted_timestamp = 'Unknown'
            
            writer.writerow([
                scan_doc.id,
                scan_data.get('type', 'Unknown'),
                scan_data.get('result', 'Unknown'),
                f"{float(scan_data.get('confidence', 0)) * 100:.1f}",
                scan_data.get('user_email', 'Unknown'),
                scan_data.get('image_name', 'Unknown'),
                formatted_timestamp,
                scan_data.get('hidden', False)
            ])
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error exporting data: {str(e)}')
        return redirect('image_analysis')

@admin_required
@csrf_exempt
def dashboard_api(request):
    """API endpoint for real-time dashboard updates"""
    if request.method == 'GET':
        try:
            # Get real-time counts
            scans_count = len(list(db.collection('scans').stream()))
            orders_count = len(list(db.collection('orders').stream()))
            
            # Calculate revenue
            orders_ref = db.collection('orders')
            delivered_orders = orders_ref.where('status', '==', 'delivered').stream()
            revenue = sum(float(o.to_dict().get('total_amount', 0)) for o in delivered_orders)
            
            # Get farms count
            farms_count = len(list(db.collection('farms').stream())) + len(SAMPLE_FARMS)
            
            return JsonResponse({
                'success': True,
                'data': {
                    'total_scans': scans_count,
                    'total_orders': orders_count,
                    'total_revenue': round(revenue, 2),
                    'total_farms': farms_count,
                    'timestamp': datetime.now(pytz.timezone('Asia/Manila')).isoformat()
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

#2ndscan

# ===============================
# SCAN-RELATED VIEWS ONLY
# ===============================

def preprocess_image(image_file):
    """Preprocess image for model prediction"""
    image = Image.open(image_file)
    image = image.convert('RGB')
    image = image.resize((224, 224))
    image_array = np.array(image) / 255.0
    image_array = np.expand_dims(image_array, axis=0)
    return image_array

def simulate_prediction(scan_type):
    """Simulate ML prediction for testing"""
    import random
    
    if scan_type == 'disease':
        classes = DISEASE_CLASSES
        recommendations = DISEASE_RECOMMENDATIONS
    else:
        classes = PEST_CLASSES
        recommendations = PEST_RECOMMENDATIONS
    
    # Simulate prediction
    predicted_class = random.choice(classes)
    confidence = random.uniform(0.75, 0.98)
    
    return predicted_class, confidence, recommendations.get(predicted_class, [])

# ===============================
# USER SCAN VIEWS
# ===============================

def scan_diagnose(request):
    """Scan and Diagnose view"""
    context = {
        'page_title': 'Scan and Diagnose',
        'description': 'Upload crop images for disease detection and analysis'
    }
    return render(request, 'user/scan_diagnose.html', context)

@csrf_exempt
def scan_image(request):
    """Handle image scanning for both users and guests"""
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            image_file = request.FILES['image']
            scan_type = request.POST.get('scan_type', 'disease')
            
            # Get user information
            uid = request.session.get('uid', 'guest')
            user_email = request.session.get('user_email', 'guest@example.com')
            user_name = request.session.get('name', 'Guest User')
            user_type = 'user' if uid != 'guest' else 'user'
            
            print(f"[DEBUG] Processing scan - UID: {uid}, Type: {scan_type}, User: {user_email}")
            
            # Check if models are available, otherwise simulate
            if disease_model and pest_model:
                # Preprocess image
                processed_image = preprocess_image(image_file)
                
                if scan_type == 'disease' and disease_model:
                    prediction = disease_model.predict(processed_image)
                    class_idx = np.argmax(prediction[0])
                    confidence = float(prediction[0][class_idx])
                    predicted_class = DISEASE_CLASSES[class_idx]
                    recommendations = DISEASE_RECOMMENDATIONS.get(predicted_class, [])
                elif scan_type == 'pest' and pest_model:
                    prediction = pest_model.predict(processed_image)
                    class_idx = np.argmax(prediction[0])
                    confidence = float(prediction[0][class_idx])
                    predicted_class = PEST_CLASSES[class_idx]
                    recommendations = PEST_RECOMMENDATIONS.get(predicted_class, [])
                else:
                    # Fallback to simulation
                    predicted_class, confidence, recommendations = simulate_prediction(scan_type)
            else:
                # Use simulation if models not available
                predicted_class, confidence, recommendations = simulate_prediction(scan_type)
            
            # Generate scan ID
            scan_id = str(uuid.uuid4())
            
            # Prepare scan data for Firestore
            scan_data = {
                'scan_id': scan_id,
                'user_id': uid,
                'user_email': user_email,
                'user_name': user_name,
                'user_type': user_type,
                'type': scan_type,
                'result': predicted_class,
                'confidence': confidence,
                'recommendations': recommendations,
                'image_name': image_file.name,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'hidden': False,  # Default to visible
                'created_at': datetime.now(pytz.timezone('Asia/Manila')).isoformat()
            }
            
            # Save to Firestore
            try:
                doc_ref = db.collection('scans').document(scan_id)
                doc_ref.set(scan_data)
                print(f"[DEBUG] Scan saved to Firestore with ID: {scan_id}")
            except Exception as firestore_error:
                print(f"[ERROR] Failed to save to Firestore: {firestore_error}")
                # Continue without Firestore for now
            
            # Return response
            response_data = {
                'success': True,
                'scan_id': scan_id,
                'type': scan_type,
                'result': predicted_class,
                'confidence': round(confidence * 100, 2),
                'recommendations': recommendations
            }
            
            print(f"[DEBUG] Scan completed successfully: {predicted_class} ({confidence:.2%})")
            return JsonResponse(response_data)
            
        except Exception as e:
            print(f"[ERROR] Scan processing error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
@csrf_exempt
def scan_history(request):
    """Get scan history for current user with preserved timestamps"""
    try:
        uid = request.session.get('uid')
        if not uid:
            return JsonResponse({'success': True, 'scans': []})

        print(f"[DEBUG] Fetching scan history for user: {uid}")

        # Get user's scans from Firestore
        scans_ref = db.collection('scans').where('user_id', '==', uid).order_by('timestamp', direction=firestore.Query.DESCENDING)

        scans = []
        for doc in scans_ref.stream():
            scan_data = doc.to_dict()
            scan_data['id'] = doc.id

            # FIXED: Preserve original timestamp without conversion
            if 'timestamp' in scan_data and scan_data['timestamp']:
                if hasattr(scan_data['timestamp'], 'seconds'):
                    # Keep Firestore timestamp format for frontend
                    scan_data['timestamp'] = {
                        'seconds': scan_data['timestamp'].seconds,
                        'nanoseconds': getattr(scan_data['timestamp'], 'nanoseconds', 0)
                    }
                # If it's already a string (ISO format), keep it as is
                elif isinstance(scan_data['timestamp'], str):
                    pass  # Keep original ISO string
                else:
                    # Convert other formats to ISO string
                    scan_data['timestamp'] = scan_data['timestamp'].isoformat()
            else:
                # Use created_at as fallback, but don't use current time
                scan_data['timestamp'] = scan_data.get('created_at', None)

            scans.append(scan_data)

        print(f"[DEBUG] Found {len(scans)} scans for user {uid}")
        return JsonResponse({'success': True, 'scans': scans})

    except Exception as e:
        print(f"[ERROR] Error getting scan history: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
def delete_user_scan(request, scan_id):
    """Delete user's scan"""
    if request.method == 'POST':
        try:
            uid = request.session.get('uid')
            if not uid:
                return JsonResponse({'success': False, 'error': 'Authentication required'})
            
            # Get scan document
            scan_ref = db.collection('scans').document(scan_id)
            scan_doc = scan_ref.get()
            
            if not scan_doc.exists:
                return JsonResponse({'success': False, 'error': 'Scan not found'})
            
            scan_data = scan_doc.to_dict()
            
            # Check if scan belongs to current user
            if scan_data.get('user_id') != uid:
                return JsonResponse({'success': False, 'error': 'Unauthorized'})
            
            # Delete the scan
            scan_ref.delete()
            print(f"[DEBUG] Scan {scan_id} deleted by user {uid}")
            
            return JsonResponse({'success': True, 'message': 'Scan deleted successfully'})
            
        except Exception as e:
            print(f"[ERROR] Error deleting scan: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# ===============================
# ADMIN SCAN VIEWS
# ===============================

@admin_required
def image_analysis(request):
    """Admin image analysis view with proper scan fetching"""
    print("[DEBUG] Admin accessing image analysis")
    
    # Initialize timezone
    tz = pytz.timezone('Asia/Manila')
    today = datetime.now(tz)
    
    try:
        # Get all scans from Firestore
        scans_ref = db.collection('scans')
        all_scans = list(scans_ref.stream())
        
        print(f"[DEBUG] Found {len(all_scans)} total scans in Firestore")
        
        # Process scans data
        scans_data = []
        disease_count = 0
        pest_count = 0
        today_count = 0
        
        # Chart data for last 7 days
        chart_data = []
        daily_counts = {}
        
        # Initialize daily counts
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            daily_counts[date.strftime('%Y-%m-%d')] = 0
        
        for doc in all_scans:
            try:
                scan_data = doc.to_dict()
                scan_data['id'] = doc.id
                
                # Handle timestamp
                timestamp = scan_data.get('timestamp')
                if timestamp:
                    if hasattr(timestamp, 'seconds'):
                        formatted_timestamp = datetime.fromtimestamp(timestamp.seconds, tz)
                    else:
                        formatted_timestamp = timestamp if hasattr(timestamp, 'strftime') else today
                else:
                    formatted_timestamp = today
                
                scan_data['timestamp'] = formatted_timestamp
                
                # Count by type
                scan_type = scan_data.get('type', 'disease')
                if scan_type == 'disease':
                    disease_count += 1
                elif scan_type == 'pest':
                    pest_count += 1
                
                # Count today's scans
                if formatted_timestamp.date() == today.date():
                    today_count += 1
                
                # Count for chart data
                scan_date_str = formatted_timestamp.strftime('%Y-%m-%d')
                if scan_date_str in daily_counts:
                    daily_counts[scan_date_str] += 1
                
                # Format data for template
                scan_data['primary_class'] = scan_data.get('result', 'Unknown')
                scan_data['primary_confidence'] = float(scan_data.get('confidence', 0)) * 100
                scan_data['username'] = scan_data.get('user_email', 'Unknown')
                scan_data['hidden'] = scan_data.get('hidden', False)
                
                scans_data.append(scan_data)
                
            except Exception as e:
                print(f"[ERROR] Error processing scan {doc.id}: {e}")
                continue
        
        # Prepare chart data
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime('%b %d')
            date_key = date.strftime('%Y-%m-%d')
            chart_data.append({
                'date': date_str,
                'count': daily_counts.get(date_key, 0)
            })
        
        # Sort scans by timestamp (newest first)
        scans_data.sort(key=lambda x: x['timestamp'], reverse=True)
        
        context = {
            'total_scans': len(scans_data),
            'disease_scans': disease_count,
            'pest_scans': pest_count,
            'today_scans': today_count,
            'scans': scans_data,
            'chart_data': json.dumps(chart_data),
        }
        
        print(f"[DEBUG] Image analysis context: Total={len(scans_data)}, Disease={disease_count}, Pest={pest_count}")
        
    except Exception as e:
        print(f"[ERROR] Error in image_analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Fallback data
        context = {
            'total_scans': 0,
            'disease_scans': 0,
            'pest_scans': 0,
            'today_scans': 0,
            'scans': [],
            'chart_data': json.dumps([]),
        }
        messages.error(request, f"Error loading scan data: {str(e)}")
    
    return render(request, 'admin/image_analysis.html', context)

@admin_required
@csrf_exempt
def toggle_scan_visibility(request, scan_id):
    """Toggle scan visibility (hide/show)"""
    if request.method == 'POST':
        try:
            scan_ref = db.collection('scans').document(scan_id)
            scan_doc = scan_ref.get()
            
            if scan_doc.exists:
                current_hidden = scan_doc.to_dict().get('hidden', False)
                scan_ref.update({'hidden': not current_hidden})
                
                action = 'hidden' if not current_hidden else 'shown'
                print(f"[DEBUG] Scan {scan_id} {action}")
                
                return JsonResponse({
                    'success': True,
                    'message': f'Scan {action} successfully',
                    'hidden': not current_hidden
                })
            else:
                return JsonResponse({'success': False, 'message': 'Scan not found'})
                
        except Exception as e:
            print(f"[ERROR] Error toggling scan visibility: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@admin_required
@csrf_exempt
def delete_scan(request, scan_id):
    """Delete a scan (admin)"""
    if request.method == 'POST':
        try:
            scan_ref = db.collection('scans').document(scan_id)
            scan_ref.delete()
            print(f"[DEBUG] Scan {scan_id} deleted by admin")
            messages.success(request, 'Scan deleted successfully')
        except Exception as e:
            print(f"[ERROR] Error deleting scan: {str(e)}")
            messages.error(request, f'Error deleting scan: {str(e)}')
        
        return redirect('image_analysis')
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@admin_required
def admin_dashboard_scans(request):
    """Admin Dashboard scan statistics only"""
    print("[DEBUG] Fetching scan statistics for admin dashboard")
    
    # Initialize default values
    scan_stats = {
        'total_scans': 0,
        'disease_scans': 0,
        'pest_scans': 0,
        'today_scans': 0,
        'recent_scans': [],
    }
    
    try:
        # Get scan counts
        scans_ref = db.collection('scans')
        all_scans = list(scans_ref.stream())
        
        total_scans = len(all_scans)
        disease_scans = len([s for s in all_scans if s.to_dict().get('type') == 'disease'])
        pest_scans = len([s for s in all_scans if s.to_dict().get('type') == 'pest'])
        
        # Count today's scans
        today = datetime.now(pytz.timezone('Asia/Manila')).date()
        today_scans = 0
        recent_scans = []
        
        # Process recent scans
        scans_by_date = sorted(all_scans, key=lambda x: x.to_dict().get('timestamp', datetime.now(pytz.timezone('Asia/Manila'))), reverse=True)
        
        for doc in scans_by_date[:5]:  # Get 5 most recent
            scan_data = doc.to_dict()
            timestamp = scan_data.get('timestamp')
            
            if timestamp:
                if hasattr(timestamp, 'seconds'):
                    scan_date = datetime.fromtimestamp(timestamp.seconds).date()
                    formatted_date = datetime.fromtimestamp(timestamp.seconds).strftime('%b %d')
                else:
                    scan_date = timestamp.date() if hasattr(timestamp, 'date') else today
                    formatted_date = timestamp.strftime('%b %d') if hasattr(timestamp, 'strftime') else 'Recent'
                
                if scan_date == today:
                    today_scans += 1
            else:
                formatted_date = 'Recent'
            
            recent_scans.append({
                'result': scan_data.get('result', 'Unknown'),
                'confidence': round(float(scan_data.get('confidence', 0)) * 100),
                'type': scan_data.get('type', 'disease'),
                'user_email': scan_data.get('user_email', 'Unknown'),
                'date': formatted_date
            })
        
        scan_stats.update({
            'total_scans': total_scans,
            'disease_scans': disease_scans,
            'pest_scans': pest_scans,
            'today_scans': today_scans,
            'recent_scans': recent_scans,
        })
        
        print(f"[DEBUG] Scan stats - Total: {total_scans}, Disease: {disease_scans}, Pest: {pest_scans}, Today: {today_scans}")
        
    except Exception as e:
        print(f"[ERROR] Error fetching scan statistics: {e}")
        # Use fallback data
    
    return scan_stats

@admin_required
def debug_firestore_collections(request):
    """Debug endpoint to see what collections exist in Firestore"""
    try:
        collections = db.collections()
        collection_info = {}
        
        for collection in collections:
            collection_name = collection.id
            try:
                docs = list(collection.limit(3).stream())
                collection_info[collection_name] = {
                    'count': len(list(collection.stream())),
                    'sample_docs': []
                }
                
                for doc in docs:
                    doc_data = doc.to_dict()
                    collection_info[collection_name]['sample_docs'].append({
                        'id': doc.id,
                        'fields': list(doc_data.keys()),
                        'sample_data': {k: str(v)[:50] for k, v in doc_data.items()}
                    })
            except Exception as e:
                collection_info[collection_name] = {'error': str(e)}
        
        return JsonResponse({
            'success': True,
            'collections': collection_info
        }, indent=2)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


#good
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model

from django.core.paginator import Paginator

User = get_user_model()

def admin_user_list(request):
    # Get all users including admins
    all_users = User.objects.all().order_by('-date_joined')
    
    # Pagination
    paginator = Paginator(all_users, 25)  # Show 25 users per page
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    
    context = {
        'users': users,
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'admin_users': User.objects.filter(is_superuser=True).count(),
        'inactive_users': User.objects.filter(is_active=False).count(),
    }
    return render(request, 'admin/user_list.html', context)


def delete_user(request, user_id):
    if not request.method == 'POST':
        messages.error(request, "Invalid request method")
        return redirect('admin_user_list')
    
    try:
        # Prevent self-deletion
        if request.user.id == user_id:
            messages.error(request, "You cannot delete your own account")
            return redirect('admin_user_list')
            
        user = User.objects.get(id=user_id)
        email = user.email
        user.delete()
        messages.success(request, f"User {email} deleted successfully")
    except User.DoesNotExist:
        messages.error(request, "User not found")
    except Exception as e:
        messages.error(request, f"Error deleting user: {str(e)}")
    
    return redirect('admin_user_list')


def edit_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        
        # Prevent editing of current user
        if user.id == request.user.id:
            messages.error(request, "You cannot edit your own account from this page")
            return redirect('admin/user_list')
            
        if request.method == 'POST':
            # Handle form submission
            form = UserEditForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, f"User {user.email} updated successfully")
                return redirect('admin/user_list')
        else:
            form = UserEditForm(instance=user)
            
        context = {
            'form': form,
            'user': user,
        }
        return render(request, 'admin/user_edit.html', context)
        
    except User.DoesNotExist:
        messages.error(request, "User not found")
        return redirect('admin/user_list')
    

#New
from types import SimpleNamespace
from datetime import datetime
from typing import Optional

from django.shortcuts import render

from .firebase_service import get_db

USERS_COLLECTION = "users"
# Adjust to your exact flag for login/registration completion
LOGIN_REGISTERED_FIELD = "login_registered"


def _ts_to_datetime(ts) -> Optional[datetime]:
    if ts is None:
        return None
    if hasattr(ts, "to_datetime"):
        return ts.to_datetime()
    if isinstance(ts, datetime):
        return ts
    return None


def _doc_to_user(doc) -> SimpleNamespace:
    data = doc.to_dict() or {}

    email = data.get("email", "")
    username = data.get("username") or (email.split("@")[0] if email else "")
    created_at = _ts_to_datetime(data.get("created_at"))
    full_name = data.get("full_name") or data.get("display_name") or ""

    return SimpleNamespace(
        id=doc.id,
        email=email,
        username=username,
        created_at=created_at,
        profile=SimpleNamespace(
            full_name=full_name,
        ),
    )

# Admin Reports Image anlysis Print

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages

from django.utils import timezone
import io
import csv
import json
from datetime import datetime, timedelta
import pytz

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch

from google.cloud import firestore


def admin_required(view_func):
    """Decorator for admin required views"""
    def wrapper(request, *args, **kwargs):
        # Add your admin check logic here
        return view_func(request, *args, **kwargs)
    return wrapper

@admin_required
def print_preview(request):
    """Print preview for scan results"""
    # Get filter parameters
    scan_type = request.GET.get('type', '')
    confidence_level = request.GET.get('confidence', '')
    date_filter = request.GET.get('date', '')
    show_hidden = request.GET.get('show_hidden', 'false') == 'true'
    
    # Get scans from Firestore with filters
    scans_ref = db.collection('scans')
    query = scans_ref.order_by('timestamp', direction=firestore.Query.DESCENDING)
    
    # Apply filters
    if scan_type:
        query = query.where('type', '==', scan_type)
    
    docs = query.stream()
    scans = []
    
    for doc in docs:
        scan_data = doc.to_dict()
        scan_data['id'] = doc.id
        
        confidence = scan_data.get('confidence', scan_data.get('primary_confidence', 0))
        if isinstance(confidence, str):
            try:
                confidence = float(confidence)
            except (ValueError, TypeError):
                confidence = 0
        # Convert to percentage - handle both decimal and already percentage values
        if confidence <= 1:
            confidence = confidence * 100
        scan_data['confidence'] = confidence
        scan_data['primary_confidence'] = confidence
        
        result = scan_data.get('result', scan_data.get('primary_class', 'No Result'))
        scan_data['result'] = result
        scan_data['primary_class'] = result
        
        username = scan_data.get('user', scan_data.get('username', 'Unknown User'))
        user_email = scan_data.get('user_email', scan_data.get('email', ''))
        
        # If no email in Firestore, try to get from Django user model
        if not user_email and username != 'Unknown User':
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user_obj = User.objects.get(username=username)
                user_email = user_obj.email
            except:
                user_email = username  # Fallback to username if email not found
        
        scan_data['username'] = username
        scan_data['user'] = username
        scan_data['user_email'] = user_email or username
        
        # Apply confidence filter
        if confidence_level:
            if confidence_level == 'high' and confidence < 80:
                continue
            elif confidence_level == 'medium' and (confidence < 60 or confidence >= 80):
                continue
            elif confidence_level == 'low' and confidence >= 60:
                continue
        
        # Apply date filter
        if date_filter:
            scan_date = scan_data.get('timestamp')
            if scan_date and hasattr(scan_date, 'date'):
                if scan_date.date().strftime('%Y-%m-%d') != date_filter:
                    continue
        
        # Apply hidden filter
        if not show_hidden and scan_data.get('hidden', False):
            continue
            
        scans.append(scan_data)
    
    # Calculate statistics
    total_scans = len(scans)
    disease_scans = len([s for s in scans if s.get('type') == 'disease'])
    pest_scans = len([s for s in scans if s.get('type') == 'pest'])
    
    # Use Asia/Manila timezone consistently
    manila_tz = pytz.timezone('Asia/Manila')
    current_time = datetime.now(manila_tz)
    
    context = {
        'scans': scans,
        'total_scans': total_scans,
        'disease_scans': disease_scans,
        'pest_scans': pest_scans,
        'print_date': current_time,
        'generated_date': current_time,
        'filters': {
            'type': scan_type,
            'confidence': confidence_level,
            'date': date_filter,
            'show_hidden': show_hidden
        }
    }
    
    return render(request, 'admin/print_preview.html', context)

@admin_required
def export_pdf(request):
    """Export scan results as PDF"""
    # Get same filtered data as print preview
    scan_type = request.GET.get('type', '')
    confidence_level = request.GET.get('confidence', '')
    date_filter = request.GET.get('date', '')
    show_hidden = request.GET.get('show_hidden', 'false') == 'true'
    
    # Get scans from Firestore with filters (same logic as print_preview)
    scans_ref = db.collection('scans')
    query = scans_ref.order_by('timestamp', direction=firestore.Query.DESCENDING)
    
    if scan_type:
        query = query.where('type', '==', scan_type)
    
    docs = query.stream()
    scans = []
    
    for doc in docs:
        scan_data = doc.to_dict()
        scan_data['id'] = doc.id
        
        confidence = scan_data.get('confidence', scan_data.get('primary_confidence', 0))
        if isinstance(confidence, str):
            try:
                confidence = float(confidence)
            except (ValueError, TypeError):
                confidence = 0
        # Convert to percentage - handle both decimal and already percentage values
        if confidence <= 1:
            confidence = confidence * 100
        scan_data['confidence'] = confidence
        scan_data['primary_confidence'] = confidence
        
        result = scan_data.get('result', scan_data.get('primary_class', 'No Result'))
        scan_data['result'] = result
        scan_data['primary_class'] = result
        
        username = scan_data.get('user', scan_data.get('username', 'Unknown User'))
        user_email = scan_data.get('user_email', scan_data.get('email', ''))
        
        # If no email in Firestore, try to get from Django user model
        if not user_email and username != 'Unknown User':
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user_obj = User.objects.get(username=username)
                user_email = user_obj.email
            except:
                user_email = username  # Fallback to username if email not found
        
        scan_data['username'] = username
        scan_data['user'] = username
        scan_data['user_email'] = user_email or username
        
        # Apply same filters as print_preview
        if confidence_level:
            if confidence_level == 'high' and confidence < 80:
                continue
            elif confidence_level == 'medium' and (confidence < 60 or confidence >= 80):
                continue
            elif confidence_level == 'low' and confidence >= 60:
                continue
        
        if date_filter:
            scan_date = scan_data.get('timestamp')
            if scan_date and hasattr(scan_date, 'date'):
                if scan_date.date().strftime('%Y-%m-%d') != date_filter:
                    continue
        
        if not show_hidden and scan_data.get('hidden', False):
            continue
            
        scans.append(scan_data)
    
    # Create PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="scan_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    # Create PDF document
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    # Build PDF content
    story = []
    
    # Title
    story.append(Paragraph("CacaoGuard - Scan Results Report", title_style))
    story.append(Spacer(1, 12))
    
    # Summary statistics
    summary_data = [
        ['Total Scans', str(len(scans))],
        ['Disease Scans', str(len([s for s in scans if s.get('type') == 'disease']))],
        ['Pest Scans', str(len([s for s in scans if s.get('type') == 'pest']))],
        ['Generated', datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')]
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Scan results table
    if scans:
        # Table headers
        data = [['Image Name', 'Type', 'Result', 'Confidence', 'User Email', 'Date']]
        
        # Table data
        for scan in scans:
            timestamp = scan.get('timestamp')
            date_str = timestamp.strftime('%Y-%m-%d %H:%M') if timestamp else 'N/A'
            
            data.append([
                scan.get('image_name', 'N/A')[:20] + '...' if len(scan.get('image_name', '')) > 20 else scan.get('image_name', 'N/A'),
                scan.get('type', 'N/A').title(),
                scan.get('result', 'N/A'),
                f"{scan.get('confidence', 0):.1f}%",
                scan.get('user_email', 'Unknown User'),  # Use user_email instead of username
                date_str
            ])
        
        # Create table
        table = Table(data, colWidths=[1.5*inch, 0.8*inch, 1.5*inch, 0.8*inch, 1*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        story.append(table)
    else:
        story.append(Paragraph("No scan results found with the applied filters.", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    
    # Get PDF data
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response

@admin_required
def image_analysis_dashboard(request):
    """Main dashboard for image analysis results"""
    try:
        # Get all scans from Firestore
        scans_ref = db.collection('scans')
        docs = scans_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
        
        scans = []
        today_count = 0
        disease_count = 0
        pest_count = 0
        
        # Use Asia/Manila timezone consistently
        manila_tz = pytz.timezone('Asia/Manila')
        today = datetime.now(manila_tz).date()
        
        for doc in docs:
            scan_data = doc.to_dict()
            scan_data['id'] = doc.id
            
            confidence = scan_data.get('confidence', scan_data.get('primary_confidence', 0))
            if isinstance(confidence, str):
                try:
                    confidence = float(confidence)
                except (ValueError, TypeError):
                    confidence = 0
            if confidence <= 1:
                confidence = confidence * 100
            confidence = round(float(confidence), 1)
            scan_data['confidence'] = confidence
            scan_data['primary_confidence'] = confidence
            
            result = scan_data.get('result', scan_data.get('primary_class', 'No Result'))
            scan_data['result'] = result
            scan_data['primary_class'] = result
            
            username = scan_data.get('user', scan_data.get('username', 'Unknown User'))
            user_email = scan_data.get('user_email', scan_data.get('email', ''))
            
            # If no email in Firestore, try to get from Django user model
            if not user_email and username != 'Unknown User':
                try:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user_obj = User.objects.get(username=username)
                    user_email = user_obj.email
                except:
                    user_email = username  # Fallback to username if email not found
            
            scan_data['username'] = username
            scan_data['user'] = username
            scan_data['user_email'] = user_email or username
            
            # Count statistics
            if scan_data.get('type') == 'disease':
                disease_count += 1
            elif scan_data.get('type') == 'pest':
                pest_count += 1
                
            # Count today's scans
            scan_date = scan_data.get('timestamp')
            if scan_date and hasattr(scan_date, 'date') and scan_date.date() == today:
                today_count += 1
                
            scans.append(scan_data)
        
        # Prepare chart data (last 7 days)
        chart_data = []
        for i in range(7):
            date = today - timedelta(days=i)
            count = len([s for s in scans if s.get('timestamp') and 
                        hasattr(s.get('timestamp'), 'date') and 
                        s.get('timestamp').date() == date])
            chart_data.append({
                'date': date.strftime('%m/%d'),
                'count': count
            })
        chart_data.reverse()
        
        context = {
            'scans': scans,
            'total_scans': len(scans),
            'disease_scans': disease_count,
            'pest_scans': pest_count,
            'today_scans': today_count,
            'chart_data': json.dumps(chart_data)
        }
        
        return render(request, 'admin/image_analysis.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading scan data: {str(e)}')
        return render(request, 'admin/image_analysis.html', {
            'scans': [],
            'total_scans': 0,
            'disease_scans': 0,
            'pest_scans': 0,
            'today_scans': 0,
            'chart_data': json.dumps([])
        })

@admin_required
def toggle_scan_visibility(request, scan_id):
    """Toggle scan visibility (hide/show)"""
    if request.method == 'POST':
        try:
            scan_ref = db.collection('scans').document(scan_id)
            scan_doc = scan_ref.get()
            
            if scan_doc.exists:
                current_hidden = scan_doc.to_dict().get('hidden', False)
                scan_ref.update({'hidden': not current_hidden})
                
                return JsonResponse({
                    'success': True,
                    'hidden': not current_hidden
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Scan not found'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@admin_required
def delete_scan(request, scan_id):
    """Delete a scan from Firestore"""
    if request.method == 'POST':
        try:
            scan_ref = db.collection('scans').document(scan_id)
            scan_ref.delete()
            messages.success(request, 'Scan deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting scan: {str(e)}')
    
    return redirect('image_analysis_dashboard')

@admin_required
def export_scan_data(request):
    """Export all scan data as CSV"""
    try:
        scans_ref = db.collection('scans')
        docs = scans_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="scan_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Image Name', 'Type', 'Primary Class', 'Confidence', 'Username', 'User Email', 'Timestamp', 'Hidden'])
        
        for doc in docs:
            scan_data = doc.to_dict()
            
            confidence = scan_data.get('confidence', scan_data.get('primary_confidence', 0))
            if isinstance(confidence, str):
                try:
                    confidence = float(confidence)
                except (ValueError, TypeError):
                    confidence = 0
            if confidence <= 1:
                confidence = confidence * 100
            confidence = round(float(confidence), 1)
                
            username = scan_data.get('user', scan_data.get('username', 'Unknown User'))
            user_email = scan_data.get('user_email', scan_data.get('email', ''))
            
            if not user_email and username != 'Unknown User':
                try:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user_obj = User.objects.get(username=username)
                    user_email = user_obj.email
                except:
                    user_email = username
            
            writer.writerow([
                doc.id,
                scan_data.get('image_name', ''),
                scan_data.get('type', ''),
                scan_data.get('primary_class', ''),
                f"{confidence:.1f}%",
                username,
                user_email or username,
                scan_data.get('timestamp', ''),
                scan_data.get('hidden', False)
            ])
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error exporting data: {str(e)}')
        return redirect('image_analysis_dashboard')

@admin_required
def debug_firestore_collections(request):
    """Debug view to check Firestore collections"""
    try:
        collections = db.collections()
        collection_info = []
        
        for collection in collections:
            docs = list(collection.limit(5).stream())
            collection_info.append({
                'name': collection.id,
                'document_count': len(list(collection.stream())),
                'sample_docs': [doc.to_dict() for doc in docs[:3]]
            })
        
        return JsonResponse({
            'success': True,
            'collections': collection_info
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


#Admin Reports Ecommerce Print
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
import pytz
from firebase_admin import firestore
import json
from calendar import monthrange
from collections import defaultdict

# Initialize Firestore


def get_customer_name(user_email):
    """Fetch customer name from users collection or order data"""
    try:
        # First try to get from users collection
        users_ref = db.collection('users')
        user_query = users_ref.where('email', '==', user_email).limit(1)
        users = list(user_query.stream())
        
        if users:
            user_data = users[0].to_dict()
            full_name = (user_data.get('full_name') or 
                        user_data.get('name') or 
                        user_data.get('displayName') or
                        f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip() or
                        f"{user_data.get('firstName', '')} {user_data.get('lastName', '')}".strip())
            
            if full_name and full_name.strip():
                return full_name.strip()
        
        # This will be handled in the calling function by checking order data
        return user_email.split('@')[0] if user_email and user_email != 'N/A' else 'Unknown Customer'
        
    except Exception as e:
        print(f"Error fetching customer name for {user_email}: {str(e)}")
        return user_email.split('@')[0] if user_email and user_email != 'N/A' else 'Unknown Customer'

import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import pytz
from datetime import datetime

@admin_required
@require_http_methods(["POST"])
def update_order_status(request):
    """Update order status with stock deduction and email notifications"""
    try:
        # ✅ Parse JSON from request body
        data = json.loads(request.body.decode("utf-8"))
        order_id = data.get("order_id")
        new_status = data.get("status")

        if not order_id or not new_status:
            return JsonResponse({"success": False, "message": "Missing order_id or status"}, status=400)

        order_ref = db.collection("orders").document(order_id)
        order_doc = order_ref.get()

        if not order_doc.exists:
            return JsonResponse({"success": False, "message": "Order not found"}, status=404)

        order_data = order_doc.to_dict()
        old_status = order_data.get("status")

        # ✅ Update Firestore
        order_ref.update({
            "status": new_status,
            "updated_at": datetime.now(pytz.timezone("Asia/Manila")),
            "updated_by": request.session.get("admin_email", "admin"),
        })

        if new_status == "delivered" and old_status != "delivered":
            deduct_stock_for_order(order_data)

        send_status_change_email(order_data, new_status)

        return JsonResponse({"success": True, "message": f"Order status updated to {new_status}"})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON data"}, status=400)
    except Exception as e:
        print(f"Error updating order status: {e}")
        return JsonResponse({"success": False, "message": str(e)}, status=500)

def deduct_stock_for_order(order_data):
    """Deduct stock quantities when order is delivered"""
    try:
        products_ref = db.collection('products')
        
        for item in order_data.get('items', []):
            product_id = item.get('product_id')
            quantity_ordered = int(item.get('quantity', 0))
            
            if not product_id:
                continue
                
            # Get current product data
            product_ref = products_ref.document(product_id)
            product_doc = product_ref.get()
            
            if product_doc.exists:
                product_data = product_doc.to_dict()
                current_stock = int(product_data.get('stock_quantity', 0))
                new_stock = max(0, current_stock - quantity_ordered)
                
                # Update stock in Firebase
                product_ref.update({
                    'stock_quantity': new_stock,
                    'last_updated': datetime.now(pytz.timezone('Asia/Manila'))
                })
                
                print(f"Stock updated for {product_data.get('name', 'Unknown Product')}: {current_stock} -> {new_stock}")
            else:
                print(f"Product {product_id} not found for stock deduction")
                
    except Exception as e:
        print(f"Error deducting stock: {str(e)}")

def admin_reports(request):
    """Generate admin reports with proper error handling"""
    try:
        # Get current date in Philippines timezone
        philippines_tz = pytz.timezone('Asia/Manila')
        now = datetime.now(philippines_tz)
        current_year = now.year
        current_month = now.month
        
        # Fetch all orders from Firestore
        orders_ref = db.collection('orders')
        all_orders = list(orders_ref.stream())
        
        # Process orders
        monthly_orders = []
        total_orders = 0
        delivered_orders = 0
        pending_orders = 0
        total_revenue = 0
        
        # For charts
        daily_sales = defaultdict(float)
        product_sales = defaultdict(int)
        
        # Track processed orders to avoid duplicates
        processed_order_ids = set()
        
        for order_doc in all_orders:
            order_data = order_doc.to_dict()
            order_id = order_doc.id
            
            # Skip if already processed
            if order_id in processed_order_ids:
                continue
            processed_order_ids.add(order_id)
            
            try:
                order_timestamp = None
                
                timestamp_fields = ['timestamp', 'created_at', 'order_date', 'date_created', 'createdAt']
                for field in timestamp_fields:
                    if field in order_data and order_data[field] is not None:
                        timestamp_value = order_data[field]
                        
                        try:
                            # Handle different timestamp formats
                            if hasattr(timestamp_value, 'timestamp'):
                                # Firestore timestamp
                                order_timestamp = datetime.fromtimestamp(timestamp_value.timestamp(), tz=philippines_tz)
                            elif isinstance(timestamp_value, str):
                                # String timestamp - try multiple formats
                                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']:
                                    try:
                                        if 'T' in timestamp_value:
                                            timestamp_value = timestamp_value.replace('Z', '')
                                        order_timestamp = datetime.strptime(timestamp_value, fmt)
                                        order_timestamp = philippines_tz.localize(order_timestamp)
                                        break
                                    except:
                                        continue
                            elif isinstance(timestamp_value, (int, float)):
                                # Unix timestamp
                                if timestamp_value > 1e10:  # Milliseconds
                                    timestamp_value = timestamp_value / 1000
                                order_timestamp = datetime.fromtimestamp(timestamp_value, tz=philippines_tz)
                            
                            if order_timestamp:
                                break
                        except Exception as e:
                            continue
                
                if not order_timestamp:
                    order_timestamp = now
                
                # Count all orders regardless of month for totals
                total_orders += 1
                
                # Get order details
                user_email = order_data.get('user_email', order_data.get('email', 'N/A'))
                
                customer_name = (order_data.get('customer_name') or 
                               order_data.get('user_name') or 
                               order_data.get('name') or
                               order_data.get('full_name') or
                               get_customer_name(user_email))
                
                amount_php = float(order_data.get('total_amount', 0))
                
                status = order_data.get('status', 'pending').lower()
                
                order_info = {
                    'id': order_doc.id,
                    'order_id': order_data.get('order_id', order_doc.id),
                    'user_email': user_email,
                    'customer_name': customer_name,
                    'total_amount': amount_php,  # Direct PHP amount from Firestore
                    'status': status,
                    'timestamp': order_timestamp,
                    'items': order_data.get('items', [])
                }
                
                # Update metrics based on status
                if status in ['delivered', 'completed', 'shipped']:
                    delivered_orders += 1
                    total_revenue += amount_php  # Direct PHP amount
                    
                    # Add to daily sales for chart (current month only)
                    if (order_timestamp.year == current_year and 
                        order_timestamp.month == current_month):
                        day_key = order_timestamp.strftime('%Y-%m-%d')
                        daily_sales[day_key] += amount_php
                elif status in ['pending', 'processing', 'confirmed']:
                    pending_orders += 1
                
                # Add to monthly orders if in current month
                if (order_timestamp.year == current_year and 
                    order_timestamp.month == current_month):
                    monthly_orders.append(order_info)
                
                # Count product sales
                for item in order_info['items']:
                    if isinstance(item, dict):
                        product_name = item.get('name', item.get('product_name', 'Unknown'))
                        quantity = item.get('quantity', item.get('qty', 1))
                        try:
                            quantity = int(quantity)
                        except:
                            quantity = 1
                        product_sales[product_name] += quantity
                        
            except Exception as e:
                continue
        
        # Sort monthly orders by timestamp (newest first)
        monthly_orders.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Prepare chart data
        chart_dates = []
        chart_sales = []
        
        # Get days in current month
        days_in_month = monthrange(current_year, current_month)[1]
        for day in range(1, days_in_month + 1):
            date_key = f"{current_year}-{current_month:02d}-{day:02d}"
            chart_dates.append(f"{current_month}/{day}")
            chart_sales.append(daily_sales.get(date_key, 0))
        
        # Get top 5 products
        top_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]
        
        context = {
            'current_month': now.strftime('%B'),
            'current_year': current_year,
            'total_orders': total_orders,
            'delivered_orders': delivered_orders,
            'pending_orders': pending_orders,
            'total_revenue': total_revenue,
            'monthly_orders': monthly_orders,
            'chart_dates': json.dumps(chart_dates),
            'chart_sales': json.dumps(chart_sales),
            'top_products': top_products,
        }
        
        return render(request, 'admin/reports.html', context)

    except Exception as e:
        context = {
            'current_month': datetime.now().strftime('%B'),
            'current_year': datetime.now().year,
            'total_orders': 0,
            'delivered_orders': 0,
            'pending_orders': 0,
            'total_revenue': 0,
            'monthly_orders': [],
            'chart_dates': json.dumps([]),
            'chart_sales': json.dumps([]),
            'top_products': [],
            'error_message': f'Error loading reports: {str(e)}',
        }
        return render(request, 'admin/reports.html', context)

def print_monthly_report(request, year, month):
    """Generate printable monthly report for specific year and month"""
    try:
        year = int(year)
        month = int(month)
        
        philippines_tz = pytz.timezone('Asia/Manila')
        
        # Fetch all orders from Firestore
        orders_ref = db.collection('orders')
        all_orders = list(orders_ref.stream())
        
        # Process orders for the specified month
        monthly_orders = []
        total_revenue = 0
        delivered_orders = 0
        total_orders = 0
        
        # Track processed orders to avoid duplicates
        processed_order_ids = set()
        
        for order_doc in all_orders:
            order_data = order_doc.to_dict()
            order_id = order_doc.id
            
            # Skip if already processed
            if order_id in processed_order_ids:
                continue
            processed_order_ids.add(order_id)
            
            try:
                order_timestamp = None
                
                timestamp_fields = ['timestamp', 'created_at', 'order_date', 'date_created', 'createdAt']
                for field in timestamp_fields:
                    if field in order_data and order_data[field] is not None:
                        timestamp_value = order_data[field]
                        
                        try:
                            if hasattr(timestamp_value, 'timestamp'):
                                order_timestamp = datetime.fromtimestamp(timestamp_value.timestamp(), tz=philippines_tz)
                            elif isinstance(timestamp_value, str):
                                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']:
                                    try:
                                        if 'T' in timestamp_value:
                                            timestamp_value = timestamp_value.replace('Z', '')
                                        order_timestamp = datetime.strptime(timestamp_value, fmt)
                                        order_timestamp = philippines_tz.localize(order_timestamp)
                                        break
                                    except:
                                        continue
                            elif isinstance(timestamp_value, (int, float)):
                                if timestamp_value > 1e10:
                                    timestamp_value = timestamp_value / 1000
                                order_timestamp = datetime.fromtimestamp(timestamp_value, tz=philippines_tz)
                            
                            if order_timestamp:
                                break
                        except Exception:
                            continue
                
                if not order_timestamp:
                    continue
                
                # Check if order is in specified month/year
                if (order_timestamp.year == year and 
                    order_timestamp.month == month):
                    
                    user_email = order_data.get('user_email', order_data.get('email', 'N/A'))
                    
                    customer_name = (order_data.get('customer_name') or 
                                   order_data.get('user_name') or 
                                   order_data.get('name') or
                                   order_data.get('full_name') or
                                   get_customer_name(user_email))
                    
                    amount_php = float(order_data.get('total_amount', 0))
                    
                    order_info = {
                        'id': order_doc.id,
                        'order_id': order_data.get('order_id', order_doc.id),
                        'user_email': user_email,
                        'customer_name': customer_name,
                        'total_amount': amount_php,  # Direct PHP amount
                        'status': order_data.get('status', 'pending').lower(),
                        'timestamp': order_timestamp,
                        'items': order_data.get('items', [])
                    }
                    
                    monthly_orders.append(order_info)
                    total_orders += 1
                    
                    if order_info['status'] in ['delivered', 'completed', 'shipped']:
                        delivered_orders += 1
                        total_revenue += amount_php  # Direct PHP amount
                        
            except Exception as e:
                continue
        
        monthly_orders.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Get month name
        month_names = [
            '', 'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        month_name = month_names[month] if 1 <= month <= 12 else 'Unknown'
        
        context = {
            'year': year,
            'month': month,
            'month_name': month_name,
            'total_orders': total_orders,
            'delivered_orders': delivered_orders,
            'total_revenue': total_revenue,
            'monthly_orders': monthly_orders,
            'report_date': datetime.now(pytz.timezone('Asia/Manila')).strftime('%B %d, %Y at %I:%M %p'),
        }
        
        return render(request, 'admin/print_monthly_report.html', context)

    except Exception as e:
        context = {
            'year': year,
            'month': month,
            'month_name': 'Unknown',
            'total_orders': 0,
            'delivered_orders': 0,
            'total_revenue': 0,
            'monthly_orders': [],
            'report_date': datetime.now().strftime('%B %d, %Y'),
            'error_message': f'Error generating report: {str(e)}',
        }
        return render(request, 'admin/print_monthly_report.html', context)

@csrf_exempt
def get_monthly_data(request):
    """API endpoint to get monthly data for AJAX requests"""
    try:
        year = int(request.GET.get('year', datetime.now().year))
        month = int(request.GET.get('month', datetime.now().month))
        
        philippines_tz = pytz.timezone('Asia/Manila')
        orders_ref = db.collection('orders')
        all_orders = list(orders_ref.stream())
        
        monthly_stats = {
            'total_orders': 0,
            'delivered_orders': 0,
            'pending_orders': 0,
            'total_revenue': 0,
            'orders': []
        }
        
        processed_order_ids = set()
        
        for order_doc in all_orders:
            order_data = order_doc.to_dict()
            order_id = order_doc.id
            
            if order_id in processed_order_ids:
                continue
            processed_order_ids.add(order_id)
            
            try:
                order_timestamp = None
                timestamp_fields = ['timestamp', 'created_at', 'order_date', 'date_created', 'createdAt']
                
                for field in timestamp_fields:
                    if field in order_data and order_data[field] is not None:
                        timestamp_value = order_data[field]
                        
                        try:
                            if hasattr(timestamp_value, 'timestamp'):
                                order_timestamp = datetime.fromtimestamp(timestamp_value.timestamp(), tz=philippines_tz)
                            elif isinstance(timestamp_value, str):
                                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']:
                                    try:
                                        if 'T' in timestamp_value:
                                            timestamp_value = timestamp_value.replace('Z', '')
                                        order_timestamp = datetime.strptime(timestamp_value, fmt)
                                        order_timestamp = philippines_tz.localize(order_timestamp)
                                        break
                                    except:
                                        continue
                            elif isinstance(timestamp_value, (int, float)):
                                if timestamp_value > 1e10:
                                    timestamp_value = timestamp_value / 1000
                                order_timestamp = datetime.fromtimestamp(timestamp_value, tz=philippines_tz)
                            
                            if order_timestamp:
                                break
                        except Exception:
                            continue
                
                if not order_timestamp:
                    continue
                
                if (order_timestamp.year == year and order_timestamp.month == month):
                    amount_php = float(order_data.get('total_amount', 0))
                    status = order_data.get('status', 'pending').lower()
                    
                    monthly_stats['total_orders'] += 1
                    
                    if status in ['delivered', 'completed', 'shipped']:
                        monthly_stats['delivered_orders'] += 1
                        monthly_stats['total_revenue'] += amount_php  # Direct PHP amount
                    elif status in ['pending', 'processing', 'confirmed']:
                        monthly_stats['pending_orders'] += 1
                        
            except Exception:
                continue
        
        return JsonResponse(monthly_stats)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

#Session
from django.shortcuts import render, redirect
from django.contrib import messages
from .decorators import admin_required, user_required, guest_required, anonymous_required

def unauthorized(request):
    """Unauthorized access page"""
    context = {
        'user_role': request.session.get('role'),
        'user_name': request.session.get('name'),
    }
    return render(request, 'errors/unauthorized.html', context)

# Custom 403 handler
def custom_403(request, exception=None):
    """Custom 403 forbidden handler"""
    context = {
        'user_role': request.session.get('role'),
        'user_name': request.session.get('name'),
    }
    return render(request, 'errors/403.html', context, status=403)

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.conf import settings
import json
import os
import uuid
from datetime import datetime, timedelta
import pytz
import firebase_admin
from firebase_admin import credentials, firestore
import logging
import traceback
import numpy as np
from PIL import Image
import random

# Initialize Firebase (assuming it's already configured)

logger = logging.getLogger(__name__)

def scan_history(request):
    """Get scan history for current user with proper formatting"""
    try:
        uid = request.session.get('uid')
        if not uid:
            return JsonResponse({'success': True, 'scans': []})

        print(f"[DEBUG] Fetching scan history for user: {uid}")

        # Get user's scans from Firestore
        scans_ref = db.collection('scans').where('user_id', '==', uid).order_by('timestamp', direction=firestore.Query.DESCENDING)
        scans = []

        for doc in scans_ref.stream():
            scan_data = doc.to_dict()
            scan_data['id'] = doc.id

            if 'confidence' in scan_data:
                confidence = scan_data['confidence']
                if isinstance(confidence, (int, float)):
                    # If confidence is between 0-1, convert to percentage
                    if confidence <= 1.0:
                        scan_data['confidence'] = round(confidence * 100, 1)
                    else:
                        scan_data['confidence'] = round(confidence, 1)

            if 'result' in scan_data:
                result_words = scan_data['result'].split()
                if len(result_words) > 2:
                    scan_data['short_name'] = ' '.join(result_words[:2])
                    scan_data['full_name'] = scan_data['result']
                else:
                    scan_data['short_name'] = scan_data['result']
                    scan_data['full_name'] = scan_data['result']

            # Handle timestamp formatting
            if 'timestamp' in scan_data and scan_data['timestamp']:
                if hasattr(scan_data['timestamp'], 'seconds'):
                    # Convert Firestore timestamp to ISO string
                    timestamp_dt = datetime.fromtimestamp(scan_data['timestamp'].seconds, tz=pytz.UTC)
                    scan_data['timestamp'] = timestamp_dt.isoformat()
                elif not isinstance(scan_data['timestamp'], str):
                    scan_data['timestamp'] = scan_data['timestamp'].isoformat()

            scans.append(scan_data)

        print(f"[DEBUG] Found {len(scans)} scans for user {uid}")
        return JsonResponse({'success': True, 'scans': scans})

    except Exception as e:
        print(f"[ERROR] Error getting scan history: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
def delete_user_scan(request, scan_id):
    """Delete user's scan with proper error handling"""
    if request.method == 'POST':
        try:
            uid = request.session.get('uid')
            if not uid:
                return JsonResponse({'success': False, 'error': 'Authentication required'})
            
            # Get scan document
            scan_ref = db.collection('scans').document(scan_id)
            scan_doc = scan_ref.get()
            
            if not scan_doc.exists:
                return JsonResponse({'success': False, 'error': 'Scan not found'})
            
            scan_data = scan_doc.to_dict()
            
            # Check if scan belongs to current user
            if scan_data.get('user_id') != uid:
                return JsonResponse({'success': False, 'error': 'Unauthorized'})
            
            # Delete the scan
            scan_ref.delete()
            print(f"[DEBUG] Scan {scan_id} deleted by user {uid}")
            
            return JsonResponse({'success': True, 'message': 'Scan deleted successfully'})
            
        except Exception as e:
            print(f"[ERROR] Error deleting scan: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def scan_details(request, scan_id):
    """Get detailed information about a specific scan"""
    try:
        uid = request.session.get('uid')
        if not uid:
            return JsonResponse({'success': False, 'error': 'Authentication required'})
        
        # Get scan document
        scan_ref = db.collection('scans').document(scan_id)
        scan_doc = scan_ref.get()
        
        if not scan_doc.exists:
            return JsonResponse({'success': False, 'error': 'Scan not found'})
        
        scan_data = scan_doc.to_dict()
        
        # Check if scan belongs to current user
        if scan_data.get('user_id') != uid:
            return JsonResponse({'success': False, 'error': 'Unauthorized'})
        
        scan_data['id'] = scan_id
        
        if 'confidence' in scan_data:
            confidence = scan_data['confidence']
            if isinstance(confidence, (int, float)):
                if confidence <= 1.0:
                    scan_data['confidence'] = round(confidence * 100, 1)
                else:
                    scan_data['confidence'] = round(confidence, 1)
        
        # Handle timestamp
        if 'timestamp' in scan_data and scan_data['timestamp']:
            if hasattr(scan_data['timestamp'], 'seconds'):
                timestamp_dt = datetime.fromtimestamp(scan_data['timestamp'].seconds, tz=pytz.UTC)
                scan_data['timestamp'] = timestamp_dt.isoformat()
        
        return JsonResponse({'success': True, 'scan': scan_data})
        
    except Exception as e:
        print(f"[ERROR] Error getting scan details: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def scan_image(request):
    """Process uploaded image for disease/pest detection"""
    if request.method == 'POST':
        try:
            if 'image' not in request.FILES:
                return JsonResponse({'success': False, 'message': 'No image provided'})
            
            image_file = request.FILES['image']
            scan_type = request.POST.get('scan_type', 'disease')
            uid = request.session.get('uid')
            
            if not uid:
                return JsonResponse({'success': False, 'message': 'Authentication required'})
            
            # Validate image
            if image_file.size > 5 * 1024 * 1024:  # 5MB limit
                return JsonResponse({'success': False, 'message': 'Image too large (max 5MB)'})
            
            # Save image temporarily
            file_extension = os.path.splitext(image_file.name)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = f"temp_scans/{unique_filename}"
            
            saved_path = default_storage.save(file_path, image_file)
            full_path = os.path.join(settings.MEDIA_ROOT, saved_path)
            
            # Mock prediction (replace with your actual model prediction)
            if scan_type == 'disease':
                classes = ['Black Pod Disease', 'Fito Disease',  'Healthy', 'Monilia Disease', 'Unknown Data', 'Mirids',]
            else:
                classes = ['Ant Weaver', 'Aphids', 'Healthy', 'Mealy Bug', 'Unknown Data', 'Pod Borer',]
            
            # Simulate prediction
            predicted_class = random.choice(classes)
            confidence_decimal = random.uniform(0.7, 0.95)  # Store as decimal
            
            confidence_percentage = round(confidence_decimal * 100, 1)
            
            # Get recommendations
            recommendations = get_recommendations(predicted_class)
            
            # Save scan to Firestore
            scan_data = {
                'user_id': uid,
                'type': scan_type,
                'result': predicted_class,
                'confidence': confidence_decimal,  # Store as decimal
                'recommendations': recommendations,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'image_path': saved_path
            }
            
            # Add to Firestore
            scan_ref = db.collection('scans').add(scan_data)
            scan_id = scan_ref[1].id
            
            # Clean up temporary file
            if os.path.exists(full_path):
                os.remove(full_path)
            
            return JsonResponse({
                'success': True,
                'result': predicted_class,
                'confidence': confidence_percentage,  # Return as percentage
                'recommendations': recommendations,
                'scan_id': scan_id
            })
            
        except Exception as e:
            print(f"[ERROR] Error processing scan: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def get_recommendations(result):
    """Get recommendations based on scan result"""
    recommendations_map = {
    # Shared Classes
    'Healthy': [
        'Continue regular monitoring',
        'Maintain good farm hygiene',
        'Keep optimal growing conditions'
    ],
    'Unknown Data': [
        'Scan unclear — please retake image',
        'Ensure good lighting and focus',
        'Upload again for accurate detection'
    ],

    # Disease Classes
    'Black Pod Disease': [
        'Remove infected pods immediately',
        'Improve drainage around trees',
        'Apply copper-based fungicide',
        'Increase air circulation'
    ],
    'Fito Disease': [
        'Prune affected branches',
        'Apply appropriate fungicide',
        'Monitor humidity levels',
        'Remove fallen debris'
    ],
    'Monilia Disease': [
        'Remove infected pods weekly',
        'Apply preventive fungicide',
        'Improve tree spacing',
        'Control humidity'
    ],
    'Mirids': [
        'Prune infested shoots',
        'Apply recommended insecticide',
        'Encourage natural predators',
        'Regular monitoring'
    ],

    # Pest Classes
    'Ant Weaver': [
        'Control ant colonies',
        'Remove ant bridges',
        'Use ant baits',
        'Maintain clean surroundings'
    ],
    'Aphids': [
        'Use beneficial insects',
        'Apply neem oil',
        'Remove affected shoots',
        'Control ant populations'
    ],
    'Mealy Bug': [
        'Apply insecticidal soap',
        'Use biological control agents',
        'Remove heavily infested parts',
        'Monitor regularly'
    ],
    'Pod Borer': [
        'Remove infested pods',
        'Use pheromone traps',
        'Apply biological control',
        'Regular monitoring'
    ]
}

    return recommendations_map.get(result, recommendations_map['Healthy'])

# New oct
@user_required
def userdashboard(request):
    """Enhanced User Dashboard with comprehensive analytics"""
    print("[DEBUG] Accessing User Dashboard:", request.session.get('user_email'), request.session.get('role'))
        
    if request.session.get('role') == 'guest':
        messages.error(request, "Guest users cannot access user dashboard.")
        return redirect('guest_dashboard')
        
    uid = request.session.get('uid')
    user_email = request.session.get('user_email')
        
    try:
        # ===== FETCH ORDERS DATA =====
        orders_ref = db.collection('orders')
        user_orders_query = orders_ref.where('firebase_uid', '==', uid)
        user_orders = list(user_orders_query.stream())
        total_orders = len(user_orders)
        pending_orders = len([o for o in user_orders if o.to_dict().get('status') == 'pending'])
        delivered_orders = len([o for o in user_orders if o.to_dict().get('status') == 'delivered'])
        total_spent = sum(float(o.to_dict().get('total_amount', 0)) for o in user_orders if o.to_dict().get('status') == 'delivered')

        # Recent orders for display
        recent_orders = []
        for doc in sorted(user_orders, key=lambda x: x.to_dict().get('created_at', datetime.now(pytz.timezone('Asia/Manila'))), reverse=True)[:5]:
            order_data = doc.to_dict()
            order_data['id'] = doc.id
            if 'created_at' in order_data and order_data['created_at']:
                if hasattr(order_data['created_at'], 'seconds'):
                    order_data['created_at'] = datetime.fromtimestamp(order_data['created_at'].seconds, tz=pytz.UTC).astimezone(pytz.timezone('Asia/Manila')),
            recent_orders.append(order_data)
                
        # ===== FETCH SCANS DATA =====
        scans_ref = db.collection('scans')
        user_scans_query = scans_ref.where('user_id', '==', uid)
        user_scans = list(user_scans_query.stream())
                
        total_scans = len(user_scans)
        disease_scans = len([s for s in user_scans if s.to_dict().get('type') == 'disease'])
        pest_scans = len([s for s in user_scans if s.to_dict().get('type') == 'pest'])
                
        recent_scans = []
        for doc in sorted(user_scans, key=lambda x: x.to_dict().get('timestamp', datetime.now(pytz.timezone('Asia/Manila'))), reverse=True)[:5]:
            scan_data = doc.to_dict()
            scan_data['id'] = doc.id
            
            # Convert confidence to percentage if it's stored as decimal (0.0-1.0)
            confidence = scan_data.get('confidence', 0)
            if isinstance(confidence, (int, float)):
                if confidence <= 1.0:
                    scan_data['confidence'] = round(confidence * 100, 1)
                else:
                    scan_data['confidence'] = round(confidence, 1)
            
            if 'timestamp' in scan_data and scan_data['timestamp']:
                if hasattr(scan_data['timestamp'], 'seconds'):
                    scan_data['timestamp'] = datetime.fromtimestamp(scan_data['timestamp'].seconds)
            recent_scans.append(scan_data)
                
        # ===== FETCH FARM MAPS DATA (FIXED) =====
        total_farm_area = sum(farm.get('area', 0) for farm in SAMPLE_FARMS)
        total_trees = sum(farm.get('trees', 0) for farm in SAMPLE_FARMS)
        total_maps = len(SAMPLE_FARMS)
        
        try:
            farms_ref = db.collection('farms')
            firebase_farms = list(farms_ref.stream())
            
            for farm_doc in firebase_farms:
                farm_data = farm_doc.to_dict()
                total_farm_area += float(farm_data.get('area', 0))
                total_trees += int(farm_data.get('trees', 0))
            
            total_maps += len(firebase_farms)
            
            print(f"[DEBUG] Farm totals - Maps: {total_maps}, Area: {total_farm_area}, Trees: {total_trees}")
            
        except Exception as farm_error:
            print(f"[ERROR] Error fetching Firebase farms: {farm_error}")
            pass
                
        # ===== PREPARE CHART DATA =====
        tz = pytz.timezone('Asia/Manila')
        today = datetime.now(tz)
        orders_chart_data = []
        scans_chart_data = []
                
        # Last 7 days data for line chart
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
                        
            daily_orders = len([
                o for o in user_orders 
                if o.to_dict().get('created_at') and
                o.to_dict()['created_at'].astimezone(tz).date() == date.date()
            ])
                        
            daily_scans = len([
                s for s in user_scans 
                if s.to_dict().get('timestamp') and
                s.to_dict()['timestamp'].astimezone(tz).date() == date.date()
            ])
                        
            orders_chart_data.append({
                'date': date_str,
                'count': daily_orders,
                'label': date.strftime('%b %d')
            })
                        
            scans_chart_data.append({
                'date': date_str,
                'count': daily_scans,
                'label': date.strftime('%b %d')
            })
        
        monthly_orders = {}
        monthly_scans = {}
        for i in range(5, -1, -1):
            month_date = today - timedelta(days=30*i)
            month_key = month_date.strftime('%b')
            monthly_orders[month_key] = 0
            monthly_scans[month_key] = 0
        
        for order in user_orders:
            order_date = order.to_dict().get('created_at')
            if order_date:
                month_key = order_date.astimezone(tz).strftime('%b')
                if month_key in monthly_orders:
                    monthly_orders[month_key] += 1
        
        for scan in user_scans:
            scan_date = scan.to_dict().get('timestamp')
            if scan_date:
                month_key = scan_date.astimezone(tz).strftime('%b')
                if month_key in monthly_scans:
                    monthly_scans[month_key] += 1
        
        monthly_chart_data = {
            'labels': list(monthly_orders.keys()),
            'orders': list(monthly_orders.values()),
            'scans': list(monthly_scans.values())
        }
        
        cancelled_orders = len([o for o in user_orders if o.to_dict().get('status') == 'cancelled'])
        processing_orders = len([o for o in user_orders if o.to_dict().get('status') == 'processing'])
        confirmed_orders = len([o for o in user_orders if o.to_dict().get('status') == 'confirmed'])
        
        order_status_distribution = {
            'pending': pending_orders,
            'processing': processing_orders,
            'delivered': delivered_orders,
            'cancelled': cancelled_orders,
            'confirmed': confirmed_orders
        }
                
        scan_distribution = {
            'disease': disease_scans,
            'pest': pest_scans
        }
                
        context = {
            'name': request.session.get('name'),
            'email': user_email,
            'role': request.session.get('role'),
            'uid': uid,
                        
            'total_orders': total_orders,
            'total_scans': total_scans,
            'total_maps': total_maps,
                        
            'pending_orders': pending_orders,
            'delivered_orders': delivered_orders,
            'total_spent': round(total_spent, 2),
            'disease_scans': disease_scans,
            'pest_scans': pest_scans,
            
            'total_farm_area': round(total_farm_area, 1),
            'total_trees': total_trees,
                        
            'recent_orders': recent_orders,
            'recent_scans': recent_scans,
            'recent_farms': SAMPLE_FARMS[:3],
                        
            'orders_chart_data': json.dumps(orders_chart_data),
            'scans_chart_data': json.dumps(scans_chart_data),
            'scan_distribution': json.dumps(scan_distribution),
            'monthly_chart_data': json.dumps(monthly_chart_data),
            'order_status_distribution': json.dumps(order_status_distribution),
                        
            'current_date': today.strftime('%Y-%m-%d'),
            'current_time': today.strftime('%H:%M:%S'),
        }
            
    except Exception as e:
        print(f"Error in userdashboard: {str(e)}")
        
        # Fallback data if Firebase fails
        fallback_area = sum(farm.get('area', 0) for farm in SAMPLE_FARMS)
        fallback_trees = sum(farm.get('trees', 0) for farm in SAMPLE_FARMS)
        fallback_maps = len(SAMPLE_FARMS)
        
        try:
            farms_ref = db.collection('farms')
            firebase_farms = list(farms_ref.stream())
            for farm_doc in firebase_farms:
                farm_data = farm_doc.to_dict()
                fallback_area += float(farm_data.get('area', 0))
                fallback_trees += int(farm_data.get('trees', 0))
            fallback_maps += len(firebase_farms)
        except:
            pass
        
        context = {
            'name': request.session.get('name'),
            'email': user_email,
            'role': request.session.get('role'),
            'uid': uid,
            'total_orders': 0,
            'total_scans': 0,
            'total_maps': fallback_maps,
            'pending_orders': 0,
            'delivered_orders': 0,
            'total_spent': 0,
            'disease_scans': 0,
            'pest_scans': 0,
            'total_farm_area': round(fallback_area, 1),
            'total_trees': fallback_trees,
            'recent_orders': [],
            'recent_scans': [],
            'recent_farms': SAMPLE_FARMS[:3],
            'orders_chart_data': json.dumps([]),
            'scans_chart_data': json.dumps([]),
            'scan_distribution': json.dumps({'disease': 0, 'pest': 0}),
            'monthly_chart_data': json.dumps({'labels': [], 'orders': [], 'scans': []}),
            'order_status_distribution': json.dumps({'pending': 0, 'processing': 0, 'delivered': 0, 'cancelled': 0}),
            'current_date': datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d'),
            'current_time': datetime.now(pytz.timezone('Asia/Manila')).strftime('%H:%M:%S'),
        }
        
    return render(request, 'user/userdashboard.html', context)

def user_orders(request):
    """Display user's orders from Firestore (excluding hidden orders)"""
    try:
        uid = request.session.get('uid')
        if not uid:
            messages.error(request, 'Please log in to view your orders.')
            return redirect('login')

        # Get all orders for this user first
        orders_ref = db.collection('orders')
        query = orders_ref.where('firebase_uid', '==', uid).order_by('created_at', direction=firestore.Query.DESCENDING)

        orders_data = []
        for doc in query.stream():
            order_data = doc.to_dict()
            order_data['id'] = doc.id
            
            # Skip hidden orders (check if hidden field exists and is True)
            if order_data.get('hidden', False):
                continue
            
            # Convert Firestore timestamp to datetime if needed
            if 'created_at' in order_data and order_data['created_at']:
                if hasattr(order_data['created_at'], 'seconds'):
                    order_data['created_at'] = datetime.fromtimestamp(order_data['created_at'].seconds, tz=pytz.UTC).astimezone(pytz.timezone('Asia/Manila'))
            
            items = order_data.get('items', [])
            for item in items:
                item['total_price'] = float(item.get('price', 0)) * int(item.get('quantity', 0))
            
            # Calculate total items
            order_data['total_items'] = len(items)
            
            orders_data.append(order_data)

        # Calculate statistics
        total_orders = len(orders_data)
        pending_orders = len([o for o in orders_data if o.get('status') == 'pending'])
        delivered_orders = len([o for o in orders_data if o.get('status') == 'delivered'])
        total_spent = sum(float(o.get('total_amount', 0)) for o in orders_data if o.get('status') == 'delivered')

        context = {
            'orders': orders_data,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'delivered_orders': delivered_orders,
            'total_spent': total_spent,
            'user_email': request.session.get('user_email', 'User'),
        }

        return render(request, 'user/orders.html', context)

    except Exception as e:
        print(f"Error fetching user orders: {str(e)}")
        messages.error(request, 'Error loading orders. Please try again.')
        return render(request, 'user/orders.html', {'orders': []})

def user_orders(request):
    """Display user's orders from Firestore (excluding hidden orders)"""
    try:
        uid = request.session.get('uid')
        if not uid:
            messages.error(request, 'Please log in to view your orders.')
            return redirect('login')

        # Get all orders for this user first
        orders_ref = db.collection('orders')
        query = orders_ref.where('firebase_uid', '==', uid).order_by('created_at', direction=firestore.Query.DESCENDING)

        orders_data = []
        for doc in query.stream():
            order_data = doc.to_dict()
            order_data['id'] = doc.id
            
            # Skip hidden orders (check if hidden field exists and is True)
            if order_data.get('hidden', False):
                continue
            
            # Convert Firestore timestamp to datetime if needed
            if 'created_at' in order_data and order_data['created_at']:
                if hasattr(order_data['created_at'], 'seconds'):
                    order_data['created_at'] = datetime.fromtimestamp(order_data['created_at'].seconds, tz=pytz.UTC).astimezone(pytz.timezone('Asia/Manila'))
            
            items = order_data.get('items', [])
            for item in items:
                item['total_price'] = float(item.get('price', 0)) * int(item.get('quantity', 0))
            
            # Calculate total items
            order_data['total_items'] = len(items)
            
            orders_data.append(order_data)

        # Calculate statistics
        total_orders = len(orders_data)
        pending_orders = len([o for o in orders_data if o.get('status') == 'pending'])
        delivered_orders = len([o for o in orders_data if o.get('status') == 'delivered'])
        total_spent = sum(float(o.get('total_amount', 0)) for o in orders_data if o.get('status') == 'delivered')

        context = {
            'orders': orders_data,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'delivered_orders': delivered_orders,
            'total_spent': total_spent,
            'user_email': request.session.get('user_email', 'User'),
        }

        return render(request, 'user/orders.html', context)

    except Exception as e:
        print(f"Error fetching user orders: {str(e)}")
        messages.error(request, 'Error loading orders. Please try again.')
        return render(request, 'user/orders.html', {'orders': []})

@admin_required
# Add this to your views.py file - Replace the admin_dashboard function

def admin_dashboard(request):
    """Enhanced Admin Dashboard with comprehensive analytics"""
    print("[DEBUG] Accessing Admin Dashboard:", request.session.get('user_email'), request.session.get('role'))
    
    # Initialize timezone
    tz = pytz.timezone('Asia/Manila')
    today = datetime.now(tz)
    
    # Initialize default values
    context = {
        'name': request.session.get('name'),
        'email': request.session.get('user_email'),
        'role': request.session.get('role'),
        'current_date': today.strftime('%Y-%m-%d'),
        'current_time': today.strftime('%H:%M:%S'),
        
        # Default values
        'total_scan_count': 0,
        'order_count': 0,
        'total_revenue': 0,
        'farm_count': len(SAMPLE_FARMS),
        
        # Recent activity
        'recent_farms': SAMPLE_FARMS[:3],
        'recent_orders': [],
        'recent_scans': [],
        
        # Chart data (initialize as empty)
        'revenue_labels': json.dumps([]),
        'revenue_data': json.dumps([]),
        'scan_labels': json.dumps([]),
        'scan_data': json.dumps([]),
        
        'disease_labels': json.dumps([]),
        'disease_data': json.dumps([]),
        'order_status_labels': json.dumps([]),
        'order_status_data': json.dumps([]),
    }
    
    try:
        # ===== FETCH SCANS DATA =====
        print("[DEBUG] Fetching scans data...")
        scans_ref = db.collection('scans')
        all_scans = list(scans_ref.stream())
        total_scan_count = len(all_scans)
        
        print(f"[DEBUG] Found {total_scan_count} total scans")
        
        # Get recent scans for activity
        recent_scans = []
        scans_by_date = sorted(all_scans, key=lambda x: x.to_dict().get('timestamp', datetime.now(pytz.timezone('Asia/Manila'))), reverse=True)
        
        disease_distribution = {}
        
        for doc in scans_by_date[:5]:
            scan_data = doc.to_dict()
            timestamp = scan_data.get('timestamp')
            if timestamp:
                if hasattr(timestamp, 'seconds'):
                    formatted_date = datetime.fromtimestamp(timestamp.seconds).strftime('%b %d')
                else:
                    formatted_date = timestamp.strftime('%b %d') if hasattr(timestamp, 'strftime') else 'Recent'
            else:
                formatted_date = 'Recent'
            
            confidence_value = float(scan_data.get('confidence', 0))
            # If confidence is between 0 and 1, multiply by 100
            if confidence_value <= 1.0:
                confidence_percentage = round(confidence_value * 100)
            else:
                confidence_percentage = round(confidence_value)
                
            recent_scans.append({
                'result': scan_data.get('result', 'Unknown'),
                'confidence': confidence_percentage,
                'type': scan_data.get('type', 'disease'),
                'date': formatted_date
            })
        
        for doc in all_scans:
            scan_data = doc.to_dict()
            result = scan_data.get('result', 'Unknown')
            disease_distribution[result] = disease_distribution.get(result, 0) + 1
        
        # Prepare disease chart data
        disease_labels = list(disease_distribution.keys())
        disease_data = list(disease_distribution.values())
        
        # Prepare scan chart data (last 7 days)
        scan_labels = []
        scan_counts = []
        
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime('%b %d')
            scan_labels.append(date_str)
            
            # Count scans for this date
            daily_scans = 0
            for scan_doc in all_scans:
                scan_data = scan_doc.to_dict()
                scan_timestamp = scan_data.get('timestamp')
                if scan_timestamp:
                    if hasattr(scan_timestamp, 'seconds'):
                        scan_date = datetime.fromtimestamp(scan_timestamp.seconds).date()
                    else:
                        scan_date = scan_timestamp.date() if hasattr(scan_timestamp, 'date') else today.date()
                    
                    if scan_date == date.date():
                        daily_scans += 1
            
            scan_counts.append(daily_scans)
        
        context.update({
            'total_scan_count': total_scan_count,
            'recent_scans': recent_scans,
            'scan_labels': json.dumps(scan_labels),
            'scan_data': json.dumps(scan_counts),
            'disease_labels': json.dumps(disease_labels),
            'disease_data': json.dumps(disease_data),
        })
        
    except Exception as e:
        print(f"[ERROR] Error fetching scans data: {e}")
        # Use fallback data for scans
        context.update({
            'total_scan_count': 45,
            'recent_scans': [
                {'result': 'Healthy', 'confidence': 95, 'type': 'disease', 'date': 'Jan 15'},
                {'result': 'Black Pod Disease', 'confidence': 87, 'type': 'disease', 'date': 'Jan 14'},
                {'result': 'Monilia Disease', 'confidence': 92, 'type': 'pest', 'date': 'Jan 13'},
                {'result': 'Healthy', 'confidence': 89, 'type': 'pest', 'date': 'Jan 12'},
                {'result': 'Frosty Pod Rot', 'confidence': 84, 'type': 'disease', 'date': 'Jan 11'},
            ],
            'scan_labels': json.dumps(['Jan 09', 'Jan 10', 'Jan 11', 'Jan 12', 'Jan 13', 'Jan 14', 'Jan 15']),
            'scan_data': json.dumps([3, 5, 8, 6, 9, 7, 12]),
            'disease_labels': json.dumps(['Healthy', 'Black Pod Disease', 'Monilia Disease', 'Frosty Pod Rot', 'Witches Broom']),
            'disease_data': json.dumps([18, 12, 8, 5, 2]),
        })
    
    try:
        # ===== FETCH ORDERS DATA =====
        print("[DEBUG] Fetching orders data...")
        orders_ref = db.collection('orders')
        all_orders = list(orders_ref.stream())
        order_count = len(all_orders)
        
        # Calculate total revenue from delivered orders
        total_revenue = 0
        recent_orders = []
        
        order_status_distribution = {
            'pending': 0,
            'confirmed': 0,
            'processing': 0,
            'delivered': 0,
            'cancelled': 0
        }
        
        orders_by_date = sorted(all_orders, key=lambda x: x.to_dict().get('created_at', datetime.now(pytz.timezone('Asia/Manila'))), reverse=True)
        
        for doc in orders_by_date:
            order_data = doc.to_dict()
            
            status = order_data.get('status', 'pending')
            if status in order_status_distribution:
                order_status_distribution[status] += 1
            
            # Add to revenue if delivered
            if status == 'delivered':
                total_revenue += float(order_data.get('total_amount', 0))
            
            # Add to recent orders (first 5)
            if len(recent_orders) < 5:
                created_at = order_data.get('created_at')
                if created_at:
                    if hasattr(created_at, 'seconds'):
                        formatted_date = datetime.fromtimestamp(created_at.seconds).strftime('%b %d')
                    else:
                        formatted_date = created_at.strftime('%b %d') if hasattr(created_at, 'strftime') else 'Recent'
                else:
                    formatted_date = 'Recent'
                
                recent_orders.append({
                    'id': doc.id,
                    'amount': float(order_data.get('total_amount', 0)),
                    'status': status,
                    'created_at': formatted_date
                })
        
        # Prepare revenue chart data (last 7 days)
        revenue_labels = []
        revenue_data = []
        
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime('%b %d')
            revenue_labels.append(date_str)
            
            # Calculate revenue for this date
            daily_revenue = 0
            for order_doc in all_orders:
                order_data = order_doc.to_dict()
                if order_data.get('status') == 'delivered':
                    order_timestamp = order_data.get('created_at')
                    if order_timestamp:
                        if hasattr(order_timestamp, 'seconds'):
                            order_date = datetime.fromtimestamp(order_timestamp.seconds).date()
                        else:
                            order_date = order_timestamp.date() if hasattr(order_timestamp, 'date') else today.date()
                        
                        if order_date == date.date():
                            daily_revenue += float(order_data.get('total_amount', 0))
            
            revenue_data.append(daily_revenue)
        
        order_status_labels = list(order_status_distribution.keys())
        order_status_data = list(order_status_distribution.values())
        
        context.update({
            'order_count': order_count,
            'total_revenue': round(total_revenue, 2),
            'recent_orders': recent_orders,
            'revenue_labels': json.dumps(revenue_labels),
            'revenue_data': json.dumps(revenue_data),
            'disease_labels': json.dumps(disease_labels),
            'disease_data': json.dumps(disease_data),
            'order_status_labels': json.dumps(order_status_labels),
            'order_status_data': json.dumps(order_status_data),
        })
        
    except Exception as e:
        print(f"[ERROR] Error fetching orders data: {e}")
        # Use fallback data for orders
        context.update({
            'order_count': 28,
            'total_revenue': 15750.00,
            'recent_orders': [
                {'id': 'ORD001', 'amount': 1250.00, 'status': 'delivered', 'created_at': 'Jan 15'},
                {'id': 'ORD002', 'amount': 890.00, 'status': 'pending', 'created_at': 'Jan 14'},
                {'id': 'ORD003', 'amount': 2100.00, 'status': 'delivered', 'created_at': 'Jan 13'},
                {'id': 'ORD004', 'amount': 675.00, 'status': 'processing', 'created_at': 'Jan 12'},
                {'id': 'ORD005', 'amount': 1450.00, 'status': 'delivered', 'created_at': 'Jan 11'},
            ],
            'revenue_labels': json.dumps(['Jan 09', 'Jan 10', 'Jan 11', 'Jan 12', 'Jan 13', 'Jan 14', 'Jan 15']),
            'revenue_data': json.dumps([1200, 2100, 1800, 2400, 1950, 2800, 3200]),
            'order_status_labels': json.dumps(['pending', 'confirmed', 'processing', 'delivered', 'cancelled']),
            'order_status_data': json.dumps([5, 3, 8, 10, 2]),
        })
    
    try:
        # ===== FETCH FARMS DATA =====
        print("[DEBUG] Fetching farms data...")
        farms_ref = db.collection('farms')
        firebase_farms = list(farms_ref.stream())
        
        # Combine Firebase farms with sample farms
        total_farm_count = len(SAMPLE_FARMS) + len(firebase_farms)
        
        # Prepare recent farms (prioritize sample farms for display)
        recent_farms = SAMPLE_FARMS[:3]
        
        context.update({
            'farm_count': total_farm_count,
            'recent_farms': recent_farms,
        })
        
    except Exception as e:
        print(f"[ERROR] Error fetching farms data: {e}")
        context.update({
            'farm_count': len(SAMPLE_FARMS),
            'recent_farms': SAMPLE_FARMS[:3],
        })
    
    print("[DEBUG] Admin Dashboard context prepared successfully")
    return render(request, 'admin/admin_dashboard.html', context)

# User management
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from firebase_admin import firestore
import json


@admin_required
def admin_user_management(request):
    """Admin user management view - shows only non-hidden registered users"""
    try:
        # Fetch all users from Firestore
        users_ref = db.collection('users')
        users_docs = users_ref.stream()
        
        users_list = []
        total_users = 0
        active_users = 0
        admin_users = 0
        regular_users = 0
        
        for doc in users_docs:
            user_data = doc.to_dict()
            user_id = doc.id
            
            # Skip hidden users
            if user_data.get('is_hidden', False):
                continue
            
            # Only include registered users (with email and name)
            if not user_data.get('email') or not user_data.get('name'):
                continue
            
            # Count statistics (excluding hidden users)
            total_users += 1
            
            # Check if user is active
            is_active = user_data.get('is_active', True)
            if is_active:
                active_users += 1
            
            # Count by role
            role = user_data.get('role', 'user')
            if role == 'admin':
                admin_users += 1
            else:
                regular_users += 1
            
            # Prepare user data for display
            users_list.append({
                'id': user_id,
                'name': user_data.get('name', 'N/A'),
                'email': user_data.get('email', 'N/A'),
                'role': role,
                'is_active': is_active,
            })
        
        # Apply search filter if provided
        search_query = request.GET.get('search', '').strip().lower()
        if search_query:
            users_list = [
                user for user in users_list
                if search_query in user['name'].lower() or search_query in user['email'].lower()
            ]
        
        # Apply role filter if provided
        role_filter = request.GET.get('role', '').strip()
        if role_filter:
            users_list = [user for user in users_list if user['role'] == role_filter]
        
        # Apply status filter if provided
        status_filter = request.GET.get('status', '').strip()
        if status_filter == 'active':
            users_list = [user for user in users_list if user['is_active']]
        elif status_filter == 'inactive':
            users_list = [user for user in users_list if not user['is_active']]
        
        context = {
            'users': users_list,
            'total_users': total_users,
            'active_users': active_users,
            'admin_users': admin_users,
            'regular_users': regular_users,
            'search_query': search_query,
            'role_filter': role_filter,
            'status_filter': status_filter,
        }
        
        return render(request, 'admin/user_management.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading users: {str(e)}')
        return render(request, 'admin/user_management.html', {
            'users': [],
            'total_users': 0,
            'active_users': 0,
            'admin_users': 0,
            'regular_users': 0,
        })


@admin_required
def hide_user(request, user_id):
    """Hide a user from the admin view (doesn't delete account or records)"""
    try:
        # Update user document to set is_hidden flag
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return JsonResponse({
                'success': False,
                'message': 'User not found'
            }, status=404)
        
        # Set is_hidden flag to True
        user_ref.update({
            'is_hidden': True
        })
        
        return JsonResponse({
            'success': True,
            'message': 'User hidden successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error hiding user: {str(e)}'
        }, status=500)


@admin_required
def unhide_user(request, user_id):
    """Unhide a user to show them in the admin view again"""
    try:
        # Update user document to set is_hidden flag to False
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return JsonResponse({
                'success': False,
                'message': 'User not found'
            }, status=404)
        
        # Set is_hidden flag to False
        user_ref.update({
            'is_hidden': False
        })
        
        return JsonResponse({
            'success': True,
            'message': 'User unhidden successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error unhiding user: {str(e)}'
        }, status=500)


