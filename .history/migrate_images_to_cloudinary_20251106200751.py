"""
Script to migrate old product images from /media/ paths to Cloudinary.

IMPORTANT: This script will:
1. Find all products with /media/ image paths
2. Prompt you to upload replacement images
3. Upload images to Cloudinary
4. Update Firestore with new Cloudinary URLs

Usage:
    python migrate_images_to_cloudinary.py
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


def find_products_with_media_paths():
    """Find all products that have /media/ paths in their images"""
    print("\n🔍 Scanning products for old /media/ image paths...")
    
    products_ref = db.collection('products')
    products_needing_migration = []
    
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
        
        # Check if any image has /media/ path
        has_media_path = False
        for img in images:
            if img and '/media/' in str(img):
                has_media_path = True
                break
        
        if has_media_path:
            products_needing_migration.append({
                'id': product['id'],
                'name': product.get('name', 'Unnamed Product'),
                'images': images
            })
    
    return products_needing_migration


def upload_image_to_cloudinary(image_path):
    """Upload a local image file to Cloudinary"""
    try:
        print(f"  📤 Uploading to Cloudinary...")
        upload_result = cloudinary.uploader.upload(
            image_path,
            folder="cacaoguard/products",
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


def migrate_product_images():
    """Main migration function"""
    print("\n" + "="*60)
    print("🚀 PRODUCT IMAGE MIGRATION TO CLOUDINARY")
    print("="*60)
    
    # Find products needing migration
    products = find_products_with_media_paths()
    
    if not products:
        print("\n✅ No products need migration! All images are already using Cloudinary or static paths.")
        return
    
    print(f"\n📋 Found {len(products)} product(s) with old /media/ paths:")
    for idx, product in enumerate(products, 1):
        print(f"\n{idx}. {product['name']} (ID: {product['id']})")
        print(f"   Current images: {product['images']}")
    
    print("\n" + "-"*60)
    print("⚠️  MIGRATION OPTIONS:")
    print("-"*60)
    print("\n1. MANUAL MODE (Recommended for a few products)")
    print("   - Script will ask you to provide local image files")
    print("   - You upload each image one by one")
    print("   - Good for: 1-5 products")
    
    print("\n2. AUTO-REPLACE WITH PLACEHOLDER")
    print("   - Automatically replace all /media/ paths with placeholder")
    print("   - You can re-upload images later via admin panel")
    print("   - Good for: Many products, will fix them later")
    
    print("\n3. SKIP (Exit)")
    print("   - Keep current /media/ paths")
    print("   - Products will show placeholder until you manually edit them")
    
    choice = input("\nChoose option (1/2/3): ").strip()
    
    if choice == '1':
        migrate_manual(products)
    elif choice == '2':
        migrate_auto_placeholder(products)
    else:
        print("\n👋 Migration skipped. You can run this script again anytime.")


def migrate_manual(products):
    """Migrate products by asking user to provide image files"""
    print("\n" + "="*60)
    print("📁 MANUAL MIGRATION MODE")
    print("="*60)
    
    for idx, product in enumerate(products, 1):
        print(f"\n--- Product {idx}/{len(products)}: {product['name']} ---")
        print(f"Product ID: {product['id']}")
        print(f"Current images: {product['images']}")
        
        print("\nOptions:")
        print("1. Upload new image(s) from your computer")
        print("2. Use placeholder image")
        print("3. Skip this product")
        
        action = input("Choose (1/2/3): ").strip()
        
        if action == '1':
            new_images = []
            num_images = int(input("How many images to upload? "))
            
            for i in range(num_images):
                image_path = input(f"  Image {i+1} - Enter full path to image file: ").strip()
                
                if os.path.exists(image_path):
                    url = upload_image_to_cloudinary(image_path)
                    if url:
                        new_images.append(url)
                else:
                    print(f"  ⚠️  File not found: {image_path}")
            
            if new_images:
                update_product_images(product['id'], new_images)
            else:
                print("  ⚠️  No images uploaded. Keeping original.")
        
        elif action == '2':
            update_product_images(product['id'], ['/static/images/placeholder-product.jpg'])
        
        else:
            print(f"  ⏭️  Skipped {product['name']}")


def migrate_auto_placeholder(products):
    """Automatically replace all /media/ paths with placeholder"""
    print("\n" + "="*60)
    print("🤖 AUTO-PLACEHOLDER MODE")
    print("="*60)
    
    confirm = input(f"\nReplace images for {len(products)} product(s) with placeholder? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("❌ Cancelled.")
        return
    
    for product in products:
        print(f"  Updating {product['name']}...")
        update_product_images(product['id'], ['/static/images/placeholder-product.jpg'])
    
    print(f"\n✅ Updated {len(products)} product(s)!")
    print("💡 You can now edit products in admin panel to upload real images.")


def update_product_images(product_id, new_images):
    """Update product images in Firestore"""
    try:
        product_ref = db.collection('products').document(product_id)
        product_ref.update({'images': new_images})
        print(f"  ✅ Updated product {product_id}")
        return True
    except Exception as e:
        print(f"  ❌ Failed to update: {e}")
        return False


if __name__ == '__main__':
    try:
        migrate_product_images()
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
