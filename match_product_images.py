"""
Interactive script to match product images from local files to Firestore products.
You'll see each product and choose which image file to upload for it.
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoguard.settings')
django.setup()

from mainapp.firebase_config import db
import cloudinary.uploader

# Get all image files
MEDIA_DIR = os.path.join(os.path.dirname(__file__), 'media', 'products')
image_files = []
if os.path.exists(MEDIA_DIR):
    image_files = [f for f in os.listdir(MEDIA_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]

print("\n" + "="*60)
print("INTERACTIVE PRODUCT IMAGE MATCHER")
print("="*60)
print(f"\n📁 Found {len(image_files)} images in media/products/")
print("Available images:")
for idx, img in enumerate(image_files, 1):
    print(f"  {idx}. {img}")

print("\n" + "-"*60)
print("OPTIONS:")
print("-"*60)
print("1. AUTO-MATCH by product name (smart matching)")
print("2. MANUAL-MATCH (you choose image for each product)")
print("3. UPLOAD ALL images and manually assign later via admin")
print("4. EXIT")

choice = input("\nChoose option (1/2/3/4): ").strip()

if choice == '1':
    print("\n🤖 AUTO-MATCHING...")
    products_ref = db.collection('products')
    
    for doc in products_ref.stream():
        product = doc.to_dict()
        product_name = product.get('name', '').lower()
        product_id = doc.id
        
        # Smart matching logic
        matched_file = None
        for img_file in image_files:
            img_name = img_file.lower().replace('.jpg', '').replace('.png', '').replace('.jpeg', '').replace('.webp', '')
            img_name = img_name.replace('_', ' ').replace('-', ' ')
            
            # Check if image name is in product name or vice versa
            if img_name in product_name or any(word in img_name for word in product_name.split() if len(word) > 3):
                matched_file = img_file
                break
        
        if matched_file:
            print(f"\n✅ {product.get('name')}")
            print(f"   Matched with: {matched_file}")
            
            # Upload to Cloudinary
            file_path = os.path.join(MEDIA_DIR, matched_file)
            try:
                upload_result = cloudinary.uploader.upload(
                    file_path,
                    folder="cacaoguard/products",
                    resource_type="image",
                    transformation=[
                        {'width': 800, 'height': 800, 'crop': 'limit'},
                        {'quality': 'auto'}
                    ]
                )
                cloudinary_url = upload_result.get('secure_url')
                
                # Update Firestore
                db.collection('products').document(product_id).update({
                    'images': [cloudinary_url]
                })
                
                print(f"   ✅ Uploaded and updated!")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        else:
            print(f"\n⚠️  {product.get('name')} - No match found, keeping placeholder")
    
    print("\n✅ AUTO-MATCHING COMPLETE!")

elif choice == '2':
    print("\n📝 MANUAL MATCHING...")
    products_ref = db.collection('products')
    
    for doc in products_ref.stream():
        product = doc.to_dict()
        product_id = doc.id
        
        print(f"\n{'='*60}")
        print(f"📦 Product: {product.get('name')}")
        print(f"   Description: {product.get('description', 'N/A')[:100]}")
        print(f"\nAvailable images:")
        for idx, img in enumerate(image_files, 1):
            print(f"  {idx}. {img}")
        
        img_choice = input(f"\nChoose image number (1-{len(image_files)}) or 's' to skip: ").strip()
        
        if img_choice.lower() == 's':
            print("⏭️  Skipped")
            continue
        
        try:
            img_idx = int(img_choice) - 1
            if 0 <= img_idx < len(image_files):
                matched_file = image_files[img_idx]
                file_path = os.path.join(MEDIA_DIR, matched_file)
                
                # Upload to Cloudinary
                upload_result = cloudinary.uploader.upload(
                    file_path,
                    folder="cacaoguard/products",
                    resource_type="image",
                    transformation=[
                        {'width': 800, 'height': 800, 'crop': 'limit'},
                        {'quality': 'auto'}
                    ]
                )
                cloudinary_url = upload_result.get('secure_url')
                
                # Update Firestore
                db.collection('products').document(product_id).update({
                    'images': [cloudinary_url]
                })
                
                print(f"✅ Uploaded {matched_file} and updated!")
            else:
                print("❌ Invalid choice")
        except Exception as e:
            print(f"❌ Error: {e}")

elif choice == '3':
    print("\n📤 UPLOADING ALL IMAGES...")
    uploaded_urls = {}
    
    for img_file in image_files:
        file_path = os.path.join(MEDIA_DIR, img_file)
        try:
            print(f"  Uploading {img_file}...")
            upload_result = cloudinary.uploader.upload(
                file_path,
                folder="cacaoguard/products",
                resource_type="image",
                transformation=[
                    {'width': 800, 'height': 800, 'crop': 'limit'},
                    {'quality': 'auto'}
                ]
            )
            uploaded_urls[img_file] = upload_result.get('secure_url')
            print(f"  ✅ {upload_result.get('secure_url')}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n✅ Uploaded {len(uploaded_urls)} images to Cloudinary!")
    print("\n💡 Now go to admin panel and edit each product to assign the correct image URL.")
    print("\nUploaded URLs:")
    for filename, url in uploaded_urls.items():
        print(f"  {filename}: {url}")

else:
    print("\n👋 Exited")
