"""
Firebase Storage backend for Django
Handles file uploads to Firebase Storage for production deployment
"""

import os
import uuid
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from firebase_admin import storage as firebase_storage
from firebase_admin import credentials
import firebase_admin
from PIL import Image
import io


class FirebaseStorage(Storage):
    """
    Firebase Storage backend for Django
    """
    
    def __init__(self):
        if not firebase_admin._apps:
            # Initialize Firebase if not already done
            # Try production path first, then local path
            cred_path = '/etc/secrets/systemcacao-firebase-adminsdk-fbsvc-126c1bf0e1.json'
            if not os.path.exists(cred_path):
                cred_path = 'mainapp/systemcacao-firebase-adminsdk-fbsvc-126c1bf0e1.json'
            
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                'storageBucket': 'systemcacao.appspot.com'
            })
        
        self.bucket = firebase_storage.bucket()
    
    def _open(self, name, mode='rb'):
        """
        Open file from Firebase Storage
        """
        try:
            blob = self.bucket.blob(name)
            file_data = blob.download_as_bytes()
            return ContentFile(file_data, name=name)
        except Exception as e:
            raise FileNotFoundError(f"File {name} not found in Firebase Storage")
    
    def _save(self, name, content):
        """
        Save file to Firebase Storage
        """
        try:
            # Optimize image if it's an image file
            if self._is_image(name):
                content = self._optimize_image(content)
            
            blob = self.bucket.blob(name)
            blob.upload_from_file(content, content_type=self._get_content_type(name))
            
            # Make the file publicly accessible
            blob.make_public()
            
            return name
        except Exception as e:
            raise Exception(f"Failed to save file to Firebase Storage: {str(e)}")
    
    def delete(self, name):
        """
        Delete file from Firebase Storage
        """
        try:
            blob = self.bucket.blob(name)
            blob.delete()
            return True
        except Exception as e:
            return False
    
    def exists(self, name):
        """
        Check if file exists in Firebase Storage
        """
        try:
            blob = self.bucket.blob(name)
            return blob.exists()
        except Exception:
            return False
    
    def listdir(self, path):
        """
        List files in a directory
        """
        try:
            blobs = self.bucket.list_blobs(prefix=path)
            files = []
            dirs = set()
            
            for blob in blobs:
                relative_path = blob.name[len(path):].lstrip('/')
                if '/' in relative_path:
                    dirs.add(relative_path.split('/')[0])
                else:
                    files.append(relative_path)
            
            return list(dirs), files
        except Exception:
            return [], []
    
    def size(self, name):
        """
        Get file size
        """
        try:
            blob = self.bucket.blob(name)
            blob.reload()
            return blob.size
        except Exception:
            return 0
    
    def url(self, name):
        """
        Get public URL for file
        """
        try:
            blob = self.bucket.blob(name)
            return blob.public_url
        except Exception:
            return None
    
    def _is_image(self, filename):
        """
        Check if file is an image
        """
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        return any(filename.lower().endswith(ext) for ext in image_extensions)
    
    def _get_content_type(self, filename):
        """
        Get content type based on file extension
        """
        ext = os.path.splitext(filename)[1].lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.csv': 'text/csv',
        }
        return content_types.get(ext, 'application/octet-stream')
    
    def _optimize_image(self, content):
        """
        Optimize image for web delivery
        """
        try:
            # Open image
            image = Image.open(content)
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            # Resize if too large (max 1920x1080)
            max_size = (1920, 1080)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save optimized image
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            return ContentFile(output.read(), name=content.name)
            
        except Exception:
            # Return original if optimization fails
            return content


class CacaoModelStorage:
    """
    Specialized storage for CacaoGuard ML models
    """
    
    def __init__(self):
        self.storage = FirebaseStorage()
        self.models_path = 'models/'
    
    def save_model(self, model_file, model_name):
        """
        Save ML model to Firebase Storage
        """
        filename = f"{self.models_path}{model_name}.pth"
        return self.storage._save(filename, model_file)
    
    def get_model_url(self, model_name):
        """
        Get public URL for model
        """
        filename = f"{self.models_path}{model_name}.pth"
        return self.storage.url(filename)
    
    def model_exists(self, model_name):
        """
        Check if model exists
        """
        filename = f"{self.models_path}{model_name}.pth"
        return self.storage.exists(filename)
    
    def list_models(self):
        """
        List all available models
        """
        try:
            _, files = self.storage.listdir(self.models_path)
            models = []
            for file in files:
                if file.endswith('.pth'):
                    model_name = file.replace('.pth', '')
                    models.append({
                        'name': model_name,
                        'url': self.get_model_url(model_name),
                        'size': self.storage.size(f"{self.models_path}{file}")
                    })
            return models
        except Exception:
            return []


# Global storage instances
firebase_storage_backend = FirebaseStorage()
cacao_model_storage = CacaoModelStorage()
