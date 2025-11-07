"""
AUTOMATIC BULK UPLOAD: All product images from media/products/ to Cloudinary

This script will:
1. Find all images in media/products/
2. Upload each one to Cloudinary
3. Update Firestore products that use these images with new Cloudinary URLs

NO MANUAL WORK NEEDED - Fully automatic!
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoguard.settings')
django.setup()

from firebase_admin import firestore
from mainapp.firebase_config import db
import json

try:
    import cloudinary.uploader
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False
    print("⚠️  Cloudinary not installed. Run: pip install cloudinary")
    sys.exit(1)


def find_all_product_images():
    """Find all images in media/products/ folder"""
    media_dir = os.path.join(os.path.dirname(__file__), 'media', 'products')
    
    if not os.path.exists(media_dir):
        print(f"❌ Media folder not found: {media_dir}")
        return []
    
    images = []
    for filename in os.listdir(media_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            full_path = os.path.join(media_dir, filename)
            images.append({
                'filename': filename,
                'path': full_path
            })
    
    return images


def upload_to_cloudinary(image_path, filename):
    """Upload image to Cloudinary"""
    try:
        print(f"  📤 Uploading {filename}...")
        upload_result = cloudinary.uploader.upload(
            image_path,
            folder="cacaoguard/products",
            public_id=os.path.splitext(filename)[0],  # Use original filename
            resource_type="image",
            transformation=[
                {'width': 800, 'height': 800, 'crop': 'limit'},
                {'quality': 'auto'}
            ]
        )
        url = upload_result.get('secure_url')
        print(f"  ✅ Uploaded: {url}")
        return url
    except Exception as e:
        print(f"  ❌ Upload failed: {e}")
        return None


def find_products_using_image(filename):
    """Find all products in Firestore that use this image filename"""
    products_ref = db.collection('products')
    matching_products = []
    
    for doc in products_ref.stream():
        product = doc.to_dict()
        product['id'] = doc.id
        
        # Check images field
        images = product.get('images', [])
        if isinstance(images, str):
            try:
                images = json.loads(images)
            except:
                images = [images] if images else []
        
        # Check if any image contains this filename
        for img in images:
            if img and filename in str(img):
                matching_products.append(product)
                break
    
    return matching_products


def update_product_image(product_id, old_images, new_cloudinary_url, filename):
    """Update product's image in Firestore - replace old path with Cloudinary URL"""
    try:
        # Replace the old /media/ path with new Cloudinary URL
        updated_images = []
        for img in old_images:
            if filename in str(img):
                updated_images.append(new_cloudinary_url)
            else:
                updated_images.append(img)
        
        product_ref = db.collection('products').document(product_id)
        product_ref.update({'images': updated_images})
        return True
    except Exception as e:
        print(f"    ⚠️  Failed to update product: {e}")
        return False


def bulk_upload():
    """Main bulk upload function"""
    print("\n" + "="*70)
    print("🚀 BULK UPLOAD: Product Images to Cloudinary")
    print("="*70)
    
    # Find all local images
    print("\n📁 Scanning media/products/ folder...")
    local_images = find_all_product_images()
    
    if not local_images:
        print("\n❌ No images found in media/products/ folder!")
        return
    
    print(f"✅ Found {len(local_images)} image(s)")
    for img in local_images:
        print(f"   - {img['filename']}")
    
    # Confirm
    print("\n" + "-"*70)
    confirm = input(f"\n📤 Upload all {len(local_images)} images to Cloudinary? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("❌ Cancelled.")
        return
    
    # Upload each image
    print("\n" + "="*70)
    print("📤 UPLOADING TO CLOUDINARY...")
    print("="*70)
    
    uploaded_count = 0
    updated_products = 0
    
    for img_info in local_images:
        filename = img_info['filename']
        path = img_info['path']
        
        print(f"\n🖼️  Processing: {filename}")
        
        # Upload to Cloudinary
        cloudinary_url = upload_to_cloudinary(path, filename)
        
        if not cloudinary_url:
            continue
        
        uploaded_count += 1
        
        # Find products using this image
        print(f"  🔍 Finding products using this image...")
        products = find_products_using_image(filename)
        
        if products:
            print(f"  📦 Found {len(products)} product(s) using this image")
            for product in products:
                print(f"    - {product.get('name', 'Unnamed')} (ID: {product['id']})")
                images = product.get('images', [])
                if isinstance(images, str):
                    try:
                        images = json.loads(images)
                    except:
                        images = [images] if images else []
                
                if update_product_image(product['id'], images, cloudinary_url, filename):
                    print(f"    ✅ Updated product {product['id']}")
                    updated_products += 1
        else:
            print(f"  ⚠️  No products found using this image (orphaned file)")
    
    # Summary
    print("\n" + "="*70)
    print("✅ BULK UPLOAD COMPLETE!")
    print("="*70)
    print(f"📤 Uploaded: {uploaded_count}/{len(local_images)} images to Cloudinary")
    print(f"📦 Updated: {updated_products} products in Firestore")
    print("\n💡 Your products should now show real images on the live site!")
    print("🌐 Check your marketplace at: https://cacaoguard2.onrender.com/guest/marketplace/")


if __name__ == '__main__':
    try:
        bulk_upload()
    except KeyboardInterrupt:
        print("\n\n⚠️  Upload cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
