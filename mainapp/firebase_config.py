# Removed pyrebase dependency - using firebase-admin instead
# firebase_config = {
#     "apiKey": "AIzaSyAs90apE9AG6k4aIg9MpJD750OsvVD70m4",
#     "authDomain": "systemcacao.firebaseapp.com",
#     "databaseURL": "https://systemcacao-default-rtdb.firebaseio.com",
#     "projectId": "systemcacao",
#     "storageBucket": "systemcacao.appspot.com",
#     "messagingSenderId": "35186667542",
#     "appId": "1:35186667542:web:14fcda24f86fee52f60537"
# }

# firebase = pyrebase.initialize_app(firebase_config)
# auth = firebase.auth()
# db = firebase.database()

import os
import firebase_admin
from firebase_admin import credentials, auth, firestore

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(BASE_DIR, "systemcacao-firebase-adminsdk-fbsvc-126c1bf0e1.json")

cred = credentials.Certificate(cred_path)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'systemcacao.appspot.com'  # ✅ This line fixes the error
    })

# Initialize Firestore client
db = firestore.client()

print("Firebase initialized with Authentication, Storage, and Firestore!")

