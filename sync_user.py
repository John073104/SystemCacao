import firebase_admin
from firebase_admin import auth, db, credentials

# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")  # path to your key file
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://systemcacao-default-rtdb.firebaseio.com'
})

def sync_users():
    users = auth.list_users().users
    ref = db.reference('users')
    for user in users:
        uid = user.uid
        user_data = ref.child(uid).get()
        if not user_data:
            # Add default data for user
            ref.child(uid).set({
                'name': user.display_name or user.email.split('@')[0],
                'email': user.email,
                'role': 'user'  # Default role
            })
            print(f"Added data for user: {uid}")

if __name__ == "__main__":
    sync_users()
    print("Users synced successfully!")