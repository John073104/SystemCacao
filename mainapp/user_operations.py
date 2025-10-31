import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoguard.settings')  # Replace with your project name
django.setup()

# Now you can safely import models
from mainapp.models import User


def main():
    print('Starting user operations...')
    
    try:
        # Fetch all users
        users = User.fetch_users()
        for user in users:
            print(f"User: {user.name}, Email: {user.email}")

        # Create a new user
        new_user = User.create_user(name="John Doe", email="john@example.com", role="Admin", status="Active")
        if new_user:
            print(f"User created: {new_user.name}")

        # Update a user
        if User.update_user(new_user.user_id, status="Inactive"):
            print("User updated successfully.")

        # Delete a user
        if User.delete_user(new_user.user_id):
            print("User deleted successfully.")
            
    except Exception as e:
        print(f"Error: {e}")
        
    print('User operations completed!')


if __name__ == '__main__':
    main()