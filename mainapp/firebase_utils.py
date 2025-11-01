import firebase_admin
from firebase_admin import credentials, firestore
from django.conf import settings
import json
from . import firebase_config

# Use Firebase already initialized in firebase_config
def initialize_firebase():
    """Return Firestore client from firebase_config"""
    # Firebase is already initialized in firebase_config
    # Just return the db instance if it exists
    if hasattr(firebase_config, 'db') and firebase_config.db:
        return firebase_config.db
    
    # If not initialized (e.g., missing credentials), try to get client
    # This will fail gracefully if Firebase isn't set up
    try:
        return firestore.client()
    except Exception as e:
        print(f"Warning: Could not get Firestore client: {e}")
        return None

class FirestoreService:
    def __init__(self):
        self.db = initialize_firebase()
    
    def add_product(self, product_data):
        """Add product to Firestore"""
        doc_ref = self.db.collection('products').document()
        product_data['id'] = doc_ref.id
        product_data['created_at'] = firestore.SERVER_TIMESTAMP
        product_data['updated_at'] = firestore.SERVER_TIMESTAMP
        doc_ref.set(product_data)
        return doc_ref.id
    
    def get_products(self, limit=None, category=None, active_only=True):
        """Get products from Firestore"""
        query = self.db.collection('products')
        
        if active_only:
            query = query.where('is_active', '==', True)
        
        if category:
            query = query.where('category', '==', category)
        
        if limit:
            query = query.limit(limit)
        
        docs = query.stream()
        products = []
        for doc in docs:
            product_data = doc.to_dict()
            # Ensure the document ID is included
            product_data['id'] = doc.id
            products.append(product_data)
        return products
    
    def get_product(self, product_id):
        """Get single product"""
        doc = self.db.collection('products').document(product_id).get()
        if doc.exists:
            product_data = doc.to_dict()
            product_data['id'] = doc.id
            return product_data
        return None
    
    def update_product(self, product_id, data):
        """Update product"""
        data['updated_at'] = firestore.SERVER_TIMESTAMP
        self.db.collection('products').document(product_id).update(data)
    
    def delete_product(self, product_id):
        """Delete product"""
        self.db.collection('products').document(product_id).delete()
    
    def add_order(self, order_data):
        """Add order to Firestore"""
        doc_ref = self.db.collection('orders').document()
        order_data['id'] = doc_ref.id
        order_data['created_at'] = firestore.SERVER_TIMESTAMP
        order_data['updated_at'] = firestore.SERVER_TIMESTAMP
        doc_ref.set(order_data)
        return doc_ref.id
    
    def get_orders(self, user_id=None, status=None):
        """Get orders"""
        query = self.db.collection('orders')
        
        if user_id:
            query = query.where('user_id', '==', user_id)
        
        if status:
            query = query.where('status', '==', status)
        
        docs = query.order_by('created_at', direction=firestore.Query.DESCENDING).stream()
        orders = []
        for doc in docs:
            order_data = doc.to_dict()
            order_data['id'] = doc.id
            orders.append(order_data)
        return orders
    
    def update_order_status(self, order_id, status):
        """Update order status"""
        self.db.collection('orders').document(order_id).update({
            'status': status,
            'updated_at': firestore.SERVER_TIMESTAMP
        })

# Initialize service
firestore_service = FirestoreService()

import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
import json
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid

# Firebase already initialized in firebase_config module
# Use the db from FirestoreService class or firebase_config
from . import firebase_config

# Get db instance from firebase_config if available
db = firebase_config.db if hasattr(firebase_config, 'db') and firebase_config.db else None

def get_user_role(uid):
    """
    Get user role from Firebase custom claims or Firestore
    """
    try:
        user = auth.get_user(uid)
        custom_claims = user.custom_claims or {}
        return custom_claims.get('role', 'user')
    except Exception as e:
        print(f"Error getting user role: {e}")
        return None

def set_user_role(uid, role):
    """
    Set user role in Firebase custom claims
    """
    try:
        auth.set_custom_user_claims(uid, {'role': role})
        return True
    except Exception as e:
        print(f"Error setting user role: {e}")
        return False

def get_user_profile(uid):
    """
    Get user profile from Firestore
    """
    try:
        doc_ref = db.collection('user_profiles').document(uid)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"Error getting user profile: {e}")
        return None

def save_user_profile(uid, profile_data):
    """
    Save user profile to Firestore
    """
    try:
        doc_ref = db.collection('user_profiles').document(uid)
        doc_ref.set(profile_data, merge=True)
        return True
    except Exception as e:
        print(f"Error saving user profile: {e}")
        return False

def delete_user_profile(uid):
    """
    Delete user profile from Firestore
    """
    try:
        doc_ref = db.collection('user_profiles').document(uid)
        doc_ref.delete()
        return True
    except Exception as e:
        print(f"Error deleting user profile: {e}")
        return False

def get_all_users():
    """
    Get all users from Firebase Auth and their profiles
    """
    try:
        users = []
        page = auth.list_users()
        
        while page:
            for user in page.users:
                profile = get_user_profile(user.uid)
                role = get_user_role(user.uid)
                
                user_data = {
                    'uid': user.uid,
                    'email': user.email,
                    'display_name': user.display_name or 'N/A',
                    'role': role or 'user',
                    'profile': profile or {}
                }
                users.append(user_data)
            
            page = page.get_next_page()
        
        return users
    except Exception as e:
        print(f"Error getting all users: {e}")
        return []

def delete_firebase_user(uid):
    """
    Delete user from Firebase Auth and Firestore
    """
    try:
        # Delete from Firebase Auth
        auth.delete_user(uid)
        # Delete profile from Firestore
        delete_user_profile(uid)
        return True
    except Exception as e:
        print(f"Error deleting Firebase user: {e}")
        return False

import firebase_admin
from firebase_admin import credentials, firestore
import base64
import os
from django.conf import settings

# Initialize Firebase if not already done
if not firebase_admin._apps:
    # Path to your service account key file
    cred = credentials.Certificate('path/to/your/serviceAccountKey.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

def upload_profile_image(uid, image_file):
    """Store profile image as base64 in Firestore"""
    try:
        # Reset file pointer to beginning
        image_file.seek(0)
        
        # Read the image file and encode as base64
        image_data = image_file.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Create data URL with proper MIME type
        mime_type = image_file.content_type
        data_url = f"data:{mime_type};base64,{base64_image}"
        
        # Store in Firestore under user's profile
        profile_ref = db.collection('user_profiles').document(uid)
        profile_ref.update({
            'profile_image': data_url,
            'profile_image_mime_type': mime_type,
            'profile_image_size': len(image_data)
        })
        
        return data_url
        
    except Exception as e:
        print(f"Error uploading profile image to Firestore: {e}")
        return None

def delete_profile_image(image_url):
    """Remove profile image from Firestore"""
    try:
        # Since we're storing in Firestore, we don't need to delete the actual file
        # The image will be removed when the profile is updated
        return True
        
    except Exception as e:
        print(f"Error deleting profile image: {e}")
        return False

def get_user_profile(uid):
    """Get user profile from Firestore"""
    try:
        profile_ref = db.collection('user_profiles').document(uid)
        profile_doc = profile_ref.get()
        
        if profile_doc.exists:
            return profile_doc.to_dict()
        else:
            return None
            
    except Exception as e:
        print(f"Error getting user profile: {e}")
        return None

def save_user_profile(uid, profile_data):
    """Save user profile to Firestore"""
    try:
        profile_ref = db.collection('user_profiles').document(uid)
        profile_ref.set(profile_data, merge=True)
        return True
        
    except Exception as e:
        print(f"Error saving user profile: {e}")
        return False

