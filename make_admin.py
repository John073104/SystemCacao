import firebase_admin
from firebase_admin import credentials, auth, db

# Initialize Firebase Admin SDK
cred = credentials.Certificate("systemcacao-firebase-adminsdk-fbsvc-126c1bf0e1.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://systemcacao-default-rtdb.firebaseio.com/'
})

def make_admin(uid):
    try:
        # Set custom claims
        auth.set_custom_user_claims(uid, {'admin': True})
        
        # Also update Realtime Database with role
        ref = db.reference(f'users/{uid}')
        ref.update({'role': 'admin'})

        print(f"User {uid} has been made an admin successfully.")
    except Exception as e:
        print(f"Error making admin: {e}")

# Replace this UID with the one you want to promote
uid_to_promote = "sHIhTL6pBgSaHCe86IAF0opFRrz1"
make_admin(uid_to_promote)

# python make_admin.py RFwQ0Cd8wGUC4L3n6ugo8WUlE9y2
                                                    