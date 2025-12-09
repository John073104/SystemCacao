"""
Check existing farms in Firestore
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoguard.settings')
django.setup()

from firebase_admin import firestore
from mainapp import firebase_config

db = firebase_config.db

print("📊 Checking farms in Firestore...\n")

farms = list(db.collection('farms').stream())

print(f"Total farms found: {len(farms)}\n")

if farms:
    for i, doc in enumerate(farms, 1):
        farm = doc.to_dict()
        print(f"{i}. {farm.get('name', 'Unknown')} - {farm.get('municipality', 'Unknown')}, {farm.get('barangay', 'Unknown')}")
        print(f"   Area: {farm.get('area', 0)} ha, Trees: {farm.get('trees', 0)}")
        print(f"   ID: {doc.id}")
        if farm.get('images'):
            print(f"   Images: {len(farm.get('images', []))} image(s)")
        print()
else:
    print("⚠️ No farms found in Firestore!")
