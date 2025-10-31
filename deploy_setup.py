#!/usr/bin/env python3
"""
Setup script for CacaoGuard deployment
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False


def setup_deployment():
    """Set up the project for deployment"""
    print("🚀 Setting up CacaoGuard for deployment...")
    
    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print("❌ Please run this script from the project root directory")
        return False
    
    # Install production dependencies
    if not run_command("pip install gunicorn whitenoise", "Installing production dependencies"):
        return False
    
    # Collect static files
    if not run_command("python manage.py collectstatic --noinput", "Collecting static files"):
        return False
    
    # Run migrations
    if not run_command("python manage.py migrate", "Running database migrations"):
        return False
    
    # Create superuser if needed
    print("👤 Creating superuser...")
    try:
        subprocess.run([
            "python", "manage.py", "createsuperuser",
            "--username", "admin",
            "--email", "admin@cacaoguard.com",
            "--noinput"
        ], check=True, input="admin123\nadmin123\n", text=True)
        print("✅ Superuser created (username: admin, password: admin123)")
    except subprocess.CalledProcessError:
        print("⚠️  Superuser creation failed or user already exists")
    
    # Upload models to Firebase Storage
    print("📦 Uploading ML models to Firebase Storage...")
    if not run_command("python manage.py upload_models --force", "Uploading models"):
        print("⚠️  Model upload failed - models will be loaded from local directory")
    
    print("\n🎉 Deployment setup completed!")
    print("\n📋 Next steps:")
    print("1. Push your code to GitHub")
    print("2. Connect your repository to Render")
    print("3. Set environment variables in Render dashboard")
    print("4. Deploy using the render.yaml configuration")
    
    return True


def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    
    # Check if required files exist
    required_files = [
        "requirements.txt",
        "render.yaml",
        "Procfile",
        "cacaoguard/settings_production.py"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Required file not found: {file}")
            return False
    
    # Check if Firebase service account key exists
    firebase_key = Path("mainapp/systemcacao-firebase-adminsdk-fbsvc-126c1bf0e1.json")
    if not firebase_key.exists():
        print("❌ Firebase service account key not found")
        print("   Please ensure the Firebase service account key is in the correct location")
        return False
    
    print("✅ All requirements met")
    return True


def main():
    """Main function"""
    print("🌱 CacaoGuard Deployment Setup")
    print("=" * 40)
    
    if not check_requirements():
        print("\n❌ Setup failed due to missing requirements")
        sys.exit(1)
    
    if not setup_deployment():
        print("\n❌ Setup failed")
        sys.exit(1)
    
    print("\n✅ Setup completed successfully!")
    print("\n📖 For detailed deployment instructions, see DEPLOYMENT.md")


if __name__ == "__main__":
    main()
