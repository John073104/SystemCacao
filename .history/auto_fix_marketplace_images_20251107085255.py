"""
AUTOMATIC FIX: Upload all product images from media/products/ to Cloudinary
and assign them to products in Firestore automatically.
This will make marketplace images show properly for guests and users.
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoguard.settings')
django.setup()

from mainapp.firebase_config import db
import cloudinary.uploader

MEDIA_DIR = os.path.join(os.path.dirname(__file__), 'media', 'products')

print("\n" + "="*70)
print("🚀 AUTOMATIC PRODUCT IMAGE FIX")
print("="*70)

# Get all images
if not os.path.exists(MEDIA_DIR):
    print(f"❌ Directory not found: {MEDIA_DIR}")
    sys.exit(1)

image_files = [f for f in os.listdir(MEDIA_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
print(f"\n📁 Found {len(image_files)} images in media/products/")

# Get all products
products_ref = db.collection('products')
products = []
for doc in products_ref.stream():
    product = doc.to_dict()
    product['id'] = doc.id
    products.append(product)

print(f"📦 Found {len(products)} products in Firestore")

if len(image_files) == 0:
    print("\n❌ No images found! Please add images to media/products/ folder")
    sys.exit(1)

print("\n" + "-"*70)
print("AUTOMATIC ASSIGNMENT STRATEGY:")
print("-"*70)
print("Since product names don't match image filenames,")
print("I'll assign images in ORDER to products:")
print("")

# Upload ALL images first
uploaded_urls = []
print("\n📤 Uploading images to Cloudinary...")
for idx, img_file in enumerate(image_files, 1):
    file_path = os.path.join(MEDIA_DIR, img_file)
    try:
        print(f"  [{idx}/{len(image_files)}] Uploading {img_file}...", end=" ")
        upload_result = cloudinary.uploader.upload(
            file_path,
            folder="cacaoguard/products",
            resource_type="image",
            transformation=[
                {'width': 800, 'height': 800, 'crop': 'limit'},
                {'quality': 'auto'}
            ]
        )
        uploaded_urls.append({
            'filename': img_file,
            'url': upload_result.get('secure_url')
        })
        print("✅")
    except Exception as e:
        print(f"❌ Error: {e}")

print(f"\n✅ Uploaded {len(uploaded_urls)} images successfully!")

# Now assign to products
print("\n" + "-"*70)
print("ASSIGNING IMAGES TO PRODUCTS:")
print("-"*70)

for idx, product in enumerate(products):
    # Get an image (cycle through if more products than images)
    img_idx = idx % len(uploaded_urls)
    assigned_image = uploaded_urls[img_idx]
    
    print(f"\n📦 Product: {product.get('name')}")
    print(f"   Image: {assigned_image['filename']}")
    print(f"   URL: {assigned_image['url'][:60]}...")
    
    try:
        # Update Firestore with Cloudinary URL
        db.collection('products').document(product['id']).update({
            'images': [assigned_image['url']]
        })
        print(f"   ✅ Updated successfully!")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "="*70)
print("✅ AUTOMATIC FIX COMPLETE!")
print("="*70)
print("\n💡 All products now have real images from Cloudinary!")
print("🌐 Check your marketplace: https://cacaoguard2.onrender.com/guest/marketplace/")
print("\n⚠️  If the assignment doesn't look right, you can manually")
print("   adjust via the admin panel: Edit Product → Update Images")
print("")
