import os
import django
import subprocess


# Set the settings module (replace 'cacaoguard.settings' with your actual project settings path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoguard.settings')

# Setup Django
django.setup()

try:
    # Create migrations
    print("Creating migrations...")
    result = subprocess.run(['python', 'manage.py', 'makemigrations', 'mainapp'], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    # Apply migrations
    print("\nApplying migrations...")
    result = subprocess.run(['python', 'manage.py', 'migrate'], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
        
except Exception as e:
    print(f"Error: {e}")
