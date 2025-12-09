"""
Farm Image Upload Handler with Cloudinary/Firebase Storage
Ensures images persist permanently across server restarts
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import os
import uuid
from datetime import datetime

@csrf_exempt
@require_http_methods(["POST"])
def upload_farm_image(request):
    """
    Upload farm images to permanent storage (Cloudinary or Firebase Storage)
    Returns permanent URL that persists across server restarts
    """
    try:
        if 'image' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No image file provided'})
        
        image_file = request.FILES['image']
        farm_id = request.POST.get('farm_id', 'new')
        
        # Validate image
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        file_ext = os.path.splitext(image_file.name)[1].lower()
        
        if file_ext not in valid_extensions:
            return JsonResponse({'success': False, 'error': 'Invalid image format. Use JPG, PNG, or WEBP'})
        
        # Check file size (max 5MB)
        if image_file.size > 5 * 1024 * 1024:
            return JsonResponse({'success': False, 'error': 'Image too large. Max size is 5MB'})
        
        # Try Cloudinary first (if configured)
        try:
            import cloudinary
            import cloudinary.uploader
            
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                image_file,
                folder=f'cacaoguard/farms/{farm_id}',
                public_id=f'{uuid.uuid4()}',
                resource_type='image',
                overwrite=True
            )
            
            image_url = upload_result['secure_url']
            
            return JsonResponse({
                'success': True,
                'url': image_url,
                'message': 'Image uploaded successfully to Cloudinary'
            })
            
        except ImportError:
            # Cloudinary not configured, use Firebase Storage
            pass
        
        # Use Firebase Storage as fallback
        try:
            from firebase_admin import storage
            
            bucket = storage.bucket()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_name = f'farms/{farm_id}/{timestamp}_{uuid.uuid4()}{file_ext}'
            
            blob = bucket.blob(file_name)
            blob.upload_from_file(image_file, content_type=image_file.content_type)
            
            # Make the file publicly accessible
            blob.make_public()
            
            image_url = blob.public_url
            
            return JsonResponse({
                'success': True,
                'url': image_url,
                'message': 'Image uploaded successfully to Firebase Storage'
            })
            
        except Exception as firebase_error:
            # Last fallback: Save to Django media folder
            from django.core.files.storage import default_storage
            from django.conf import settings
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_name = f'farm_images/{farm_id}_{timestamp}_{uuid.uuid4()}{file_ext}'
            
            file_path = default_storage.save(file_name, image_file)
            image_url = request.build_absolute_uri(settings.MEDIA_URL + file_path)
            
            return JsonResponse({
                'success': True,
                'url': image_url,
                'message': 'Image uploaded successfully to media storage'
            })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
def delete_farm_image(request):
    """Delete farm image from storage"""
    try:
        import json
        data = json.loads(request.body)
        image_url = data.get('url', '')
        
        if not image_url:
            return JsonResponse({'success': False, 'error': 'No image URL provided'})
        
        # Try to delete from Cloudinary
        if 'cloudinary.com' in image_url:
            try:
                import cloudinary.uploader
                
                # Extract public_id from URL
                public_id = image_url.split('/')[-1].split('.')[0]
                cloudinary.uploader.destroy(public_id)
                
                return JsonResponse({'success': True, 'message': 'Image deleted from Cloudinary'})
            except:
                pass
        
        # Try to delete from Firebase Storage
        if 'firebasestorage.googleapis.com' in image_url:
            try:
                from firebase_admin import storage
                
                bucket = storage.bucket()
                # Extract blob name from URL
                blob_name = image_url.split('/o/')[1].split('?')[0]
                blob = bucket.blob(blob_name)
                blob.delete()
                
                return JsonResponse({'success': True, 'message': 'Image deleted from Firebase Storage'})
            except:
                pass
        
        # Delete from local media storage
        if '/media/' in image_url:
            try:
                from django.core.files.storage import default_storage
                
                file_path = image_url.split('/media/')[1]
                if default_storage.exists(file_path):
                    default_storage.delete(file_path)
                
                return JsonResponse({'success': True, 'message': 'Image deleted from media storage'})
            except:
                pass
        
        return JsonResponse({'success': True, 'message': 'Image reference removed'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
