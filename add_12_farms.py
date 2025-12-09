"""
Add 12 Complete Farms for Oriental Mindoro
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoguard.settings')
django.setup()

from firebase_admin import firestore
from mainapp import firebase_config

db = firebase_config.db

# 12 Farms across Oriental Mindoro municipalities
FARMS_DATA = [
    {
        'name': 'Barangay Poblacion Cacao Farm',
        'municipality': 'Victoria',
        'barangay': 'Poblacion',
        'area': 4.5,
        'trees': 520,
        'status': 'Active',
        'lat': 13.1375,
        'lng': 121.2410,
        'description': 'Primary cacao growing area with established farms and modern farming techniques',
        'contact': 'Brgy. Captain Juan Santos - 0917-123-4567',
        'images': ['/static/images/download (2).jpg', '/static/images/download (1).jpg']
    },
    {
        'name': 'San Vicente Heritage Farm',
        'municipality': 'Victoria',
        'barangay': 'San Vicente',
        'area': 3.2,
        'trees': 430,
        'status': 'Active',
        'lat': 13.1500,
        'lng': 121.2333,
        'description': 'Emerging farming community with traditional and modern cacao cultivation methods',
        'contact': 'Brgy. Captain Maria Cruz - 0918-234-5678',
        'images': ['/static/images/download (1).jpg', '/static/images/download.jpg']
    },
    {
        'name': 'Macatoc Production Facility',
        'municipality': 'Victoria',
        'barangay': 'Macatoc',
        'area': 5.8,
        'trees': 650,
        'status': 'Active',
        'lat': 13.1440,
        'lng': 121.2320,
        'description': 'Large scale cacao production facility with processing center',
        'contact': 'Farm Manager Pedro Reyes - 0919-345-6789',
        'images': ['/static/images/download (3).jpg', '/static/images/download (2).jpg']
    },
    {
        'name': 'Calapan City Organic Farm',
        'municipality': 'Calapan',
        'barangay': 'San Antonio',
        'area': 6.2,
        'trees': 780,
        'status': 'Active',
        'lat': 13.4117,
        'lng': 121.1803,
        'description': 'Certified organic cacao farm implementing sustainable farming practices',
        'contact': 'Mr. Roberto Santos - 0920-456-7890',
        'images': ['/static/images/download.jpg', '/static/images/download (1).jpg']
    },
    {
        'name': 'Naujan Valley Cacao Plantation',
        'municipality': 'Naujan',
        'barangay': 'Bagumbayan',
        'area': 7.5,
        'trees': 920,
        'status': 'Active',
        'lat': 13.3219,
        'lng': 121.3031,
        'description': 'Expansive cacao plantation in the fertile Naujan valley region',
        'contact': 'Mrs. Elena Garcia - 0921-567-8901',
        'images': ['/static/images/download (2).jpg', '/static/images/download (3).jpg']
    },
    {
        'name': 'Baco Community Farm',
        'municipality': 'Baco',
        'barangay': 'Poblacion',
        'area': 4.8,
        'trees': 550,
        'status': 'Active',
        'lat': 13.3553,
        'lng': 121.0972,
        'description': 'Community-managed cacao farm supporting local farmers',
        'contact': 'Brgy. Captain Jose Mendoza - 0922-678-9012',
        'images': ['/static/images/download (1).jpg', '/static/images/download (2).jpg']
    },
    {
        'name': 'Puerto Galera Hillside Farm',
        'municipality': 'Puerto Galera',
        'barangay': 'San Isidro',
        'area': 3.5,
        'trees': 380,
        'status': 'Monitoring',
        'lat': 13.5061,
        'lng': 120.9542,
        'description': 'Hillside cacao farm with scenic views and eco-tourism potential',
        'contact': 'Mr. Antonio dela Cruz - 0923-789-0123',
        'images': ['/static/images/download (3).jpg', '/static/images/download.jpg']
    },
    {
        'name': 'Roxas Cooperative Farm',
        'municipality': 'Roxas',
        'barangay': 'San Mariano',
        'area': 8.2,
        'trees': 1050,
        'status': 'Active',
        'lat': 12.5897,
        'lng': 121.5172,
        'description': 'Large cooperative farm managed by local farmers association',
        'contact': 'Coop Chairman Luis Ramirez - 0924-890-1234',
        'images': ['/static/images/download (2).jpg', '/static/images/download (1).jpg']
    },
    {
        'name': 'Pinamalayan Upland Farm',
        'municipality': 'Pinamalayan',
        'barangay': 'Pili',
        'area': 5.5,
        'trees': 680,
        'status': 'Active',
        'lat': 13.0436,
        'lng': 121.4753,
        'description': 'Upland cacao farm utilizing terracing and soil conservation',
        'contact': 'Mr. Ricardo Torres - 0925-901-2345',
        'images': ['/static/images/download.jpg', '/static/images/download (3).jpg']
    },
    {
        'name': 'Bongabong Agroforestry Site',
        'municipality': 'Bongabong',
        'barangay': 'Labasan',
        'area': 6.8,
        'trees': 850,
        'status': 'Active',
        'lat': 12.7133,
        'lng': 121.3700,
        'description': 'Integrated agroforestry system with cacao as primary crop',
        'contact': 'Mrs. Carmen Flores - 0926-012-3456',
        'images': ['/static/images/download (1).jpg', '/static/images/download (2).jpg']
    },
    {
        'name': 'Socorro Coastal Farm',
        'municipality': 'Socorro',
        'barangay': 'Catiningan',
        'area': 4.2,
        'trees': 480,
        'status': 'Active',
        'lat': 12.5739,
        'lng': 121.4092,
        'description': 'Coastal cacao farm with unique microclimate conditions',
        'contact': 'Brgy. Captain Miguel Santos - 0927-123-4567',
        'images': ['/static/images/download (3).jpg', '/static/images/download.jpg']
    },
    {
        'name': 'Mansalay Forest Edge Farm',
        'municipality': 'Mansalay',
        'barangay': 'Poblacion',
        'area': 7.0,
        'trees': 890,
        'status': 'Monitoring',
        'lat': 12.5167,
        'lng': 121.4333,
        'description': 'Forest-edge farm practicing sustainable shade-grown cacao cultivation',
        'contact': 'Mr. Fernando Aquino - 0928-234-5678',
        'images': ['/static/images/download (2).jpg', '/static/images/download (3).jpg']
    }
]

def add_12_farms():
    print("🌴 ADDING 12 ORIENTAL MINDORO CACAO FARMS\n")
    print("=" * 60)
    
    # Delete existing farms
    existing = list(db.collection('farms').stream())
    if existing:
        print(f"\n🗑️  Deleting {len(existing)} existing farm(s)...")
        for doc in existing:
            doc.reference.delete()
        print("✅ Cleanup complete\n")
    
    # Add 12 farms
    print(f"📤 Adding {len(FARMS_DATA)} farms to Firestore...\n")
    
    added_count = 0
    for farm in FARMS_DATA:
        farm_data = {
            **farm,
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref = db.collection('farms').add(farm_data)
        added_count += 1
        print(f"  {added_count}. ✅ {farm['name']}")
        print(f"      📍 {farm['municipality']}, {farm['barangay']}")
        print(f"      🌳 {farm['trees']} trees on {farm['area']} hectares")
        print(f"      🆔 {doc_ref[1].id}\n")
    
    print("=" * 60)
    print(f"\n🎉 SUCCESS! {added_count} farms added to Firestore")
    
    # Verification
    print("\n📊 VERIFICATION:")
    all_farms = list(db.collection('farms').stream())
    print(f"   Total farms in database: {len(all_farms)}")
    
    # Group by municipality
    by_municipality = {}
    for doc in all_farms:
        farm = doc.to_dict()
        municipality = farm.get('municipality', 'Unknown')
        by_municipality[municipality] = by_municipality.get(municipality, 0) + 1
    
    print("\n   📍 Farms by Municipality:")
    for municipality, count in sorted(by_municipality.items()):
        print(f"      • {municipality}: {count} farm(s)")
    
    print("\n✨ All farms are now live in Firestore!")
    print("🔄 Refresh your admin page to see all 12 farms\n")

if __name__ == '__main__':
    add_12_farms()
