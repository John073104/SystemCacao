"""
Migrate SAMPLE_FARMS data to Firestore
Run this once to populate Firestore with initial farm data
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoguard.settings')
django.setup()

from firebase_admin import firestore
from mainapp import firebase_config

db = firebase_config.db

# Sample farms from views.py
SAMPLE_FARMS = [
    {
        'name': 'Barangay Poblacion Farm',
        'municipality': 'Victoria',
        'barangay': 'Poblacion',
        'area': 4.5,
        'trees': 520,
        'status': 'Active',
        'lat': 13.1375,
        'lng': 121.2410,
        'description': 'Primary cacao growing area with established farms',
        'contact': 'Brgy. Captain Juan Santos',
        'images': [
            '/static/images/download (2).jpg',
            '/static/images/download (1).jpg',
            '/static/images/download (3).jpg'
        ]
    },
    {
        'name': 'San Vicente Cacao Farm',
        'municipality': 'Victoria',
        'barangay': 'San Vicente',
        'area': 3.2,
        'trees': 430,
        'status': 'Active',
        'lat': 13.1500,
        'lng': 121.2333,
        'description': 'Emerging farming community with modern techniques',
        'contact': 'Brgy. Captain Maria Cruz',
        'images': [
            '/static/images/download (1).jpg',
            '/static/images/download.jpg'
        ]
    },
    {
        'name': 'Macatoc Cacao Farm',
        'municipality': 'Victoria',
        'barangay': 'Macatoc',
        'area': 5.8,
        'trees': 650,
        'status': 'Active',
        'lat': 13.1250,
        'lng': 121.2500,
        'description': 'Large scale cacao production facility',
        'contact': 'Farm Manager Pedro Reyes',
        'images': [
            '/static/images/download (3).jpg',
            '/static/images/download (2).jpg'
        ]
    }
]

def migrate_to_firestore():
    print("🚀 Starting SAMPLE_FARMS migration to Firestore...")
    
    # Check if farms already exist
    existing_farms = list(db.collection('farms').limit(1).stream())
    
    if existing_farms:
        print("⚠️  Farms already exist in Firestore!")
        response = input("Do you want to REPLACE all existing farms? (yes/no): ")
        
        if response.lower() == 'yes':
            print("🗑️  Deleting existing farms...")
            for doc in db.collection('farms').stream():
                doc.reference.delete()
            print("✅ Existing farms deleted")
        else:
            print("❌ Migration cancelled")
            return
    
    # Add SAMPLE_FARMS to Firestore
    print(f"\n📤 Uploading {len(SAMPLE_FARMS)} farms to Firestore...")
    
    for farm in SAMPLE_FARMS:
        farm_data = {
            **farm,
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref = db.collection('farms').add(farm_data)
        print(f"  ✅ Added: {farm['name']} (ID: {doc_ref[1].id})")
    
    print(f"\n🎉 Migration complete! {len(SAMPLE_FARMS)} farms added to Firestore")
    print("\n📊 Verification:")
    
    # Verify
    all_farms = list(db.collection('farms').stream())
    print(f"   Total farms in Firestore: {len(all_farms)}")
    
    for doc in all_farms:
        farm = doc.to_dict()
        print(f"   - {farm.get('name')} ({farm.get('municipality')})")

if __name__ == '__main__':
    migrate_to_firestore()
