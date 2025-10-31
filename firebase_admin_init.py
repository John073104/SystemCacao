import firebase_admin
from firebase_admin import credentials

# Initialize Firebase Admin
cred = credentials.Certificate("systemcacao-firebase-adminsdk-fbsvc-126c1bf0e1.json")  
firebase_admin.initialize_app(cred)
