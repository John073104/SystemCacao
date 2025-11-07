"""Check what images products have in Firestore"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoguard.settings')
django.setup()

from mainapp.firebase_config import db

print("\n" + "="*60)
print("CURRENT PRODUCTS IN FIRESTORE")
print("="*60)

products_ref = db.collection('products')
for doc in products_ref.stream():
    product = doc.to_dict()
    print(f"\n📦 {product.get('name', 'Unnamed')}")
    print(f"   ID: {doc.id}")
    print(f"   Images: {product.get('images', [])}")
