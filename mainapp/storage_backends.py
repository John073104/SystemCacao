from django.core.files.storage import default_storage
from django.conf import settings
import os
import uuid
from PIL import Image
import io

class CacaoImageStorage:
    """Custom storage handler for cacao scan images"""
    
    def __init__(self):
        self.storage = default_storage
    
    def save_scan_image(self, image_file, user_id, scan_type):
        """
        Save scan image with proper naming and optimization
        """
        # Generate unique filename
        file_extension = os.path.splitext(image_file.name)[1].lower()
        unique_filename = f"{scan_type}_{user_id}_{uuid.uuid4().hex}{file_extension}"
        
        # Create path with date organization
        from datetime import datetime
        date_path = datetime.now().strftime('%Y/%m/%d')
        file_path = f"scans/{date_path}/{unique_filename}"
        
        # Optimize image before saving
        optimized_image = self.optimize_image(image_file)
        
        # Save to storage
        saved_path = self.storage.save(file_path, optimized_image)
        return saved_path
    
    def optimize_image(self, image_file):
        """Optimize image size and quality"""
        try:
            # Open image
            image = Image.open(image_file)
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            # Resize if too large
            max_size = getattr(settings, 'MAX_IMAGE_SIZE', (1024, 1024))
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save optimized image to bytes
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            # Create Django file object
            from django.core.files.base import ContentFile
            return ContentFile(output.read(), name=image_file.name)
            
        except Exception as e:
            # Return original if optimization fails
            return image_file
    
    def delete_scan_image(self, image_path):
        """Delete scan image from storage"""
        if image_path and self.storage.exists(image_path):
            self.storage.delete(image_path)
            return True
        return False
    
    def get_image_url(self, image_path):
        """Get public URL for image"""
        if image_path:
            return self.storage.url(image_path)
        return None

from django.contrib.auth import get_user_model
from firebase_admin import auth as firebase_auth

User = get_user_model()

class FirebaseBackend:
    def authenticate(self, request, uid=None):
        try:
            # Get Firebase user data
            firebase_user = firebase_auth.get_user(uid)
            email = firebase_user.email
            
            # Get or create Django user
            user, created = User.objects.get_or_create(
                username=email,
                defaults={
                    'email': email,
                    'uid': uid,
                    'is_active': True
                }
            )
            
            if not created:
                # Update existing user if needed
                if user.uid != uid:
                    user.uid = uid
                    user.save()
            
            return user
            
        except Exception as e:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None