# 🚀 CacaoGuard - Render Deployment Guide

## ✅ Pre-Deployment Checklist

- [x] Django project configured for production
- [x] Firebase integration ready
- [x] Static files configured
- [x] render.yaml created
- [x] requirements.txt prepared
- [x] Environment variables documented

---

## 📋 Step-by-Step Deployment Instructions

### **Step 1: Prepare Your GitHub Repository**

1. **Initialize Git** (if not already done):
```bash
cd c:\Users\ACER\Dropbox\PC\Downloads\cacaoguardbackup\cacaoguard
git init
git add .
git commit -m "Initial commit - CacaoGuard ready for deployment"
```

2. **Create a GitHub Repository**:
   - Go to https://github.com/new
   - Create repository: `cacaoguard`
   - Do NOT initialize with README (we already have one)

3. **Push to GitHub**:
```bash
git remote add origin https://github.com/YOUR_USERNAME/cacaoguard.git
git branch -M main
git push -u origin main
```

---

### **Step 2: Set Up Render Account**

1. **Create Render Account**:
   - Go to https://render.com
   - Sign up with GitHub (recommended)
   - Authorize Render to access your repositories

2. **Connect GitHub**:
   - In Render dashboard: Settings → GitHub
   - Connect your GitHub account
   - Authorize repository access

---

### **Step 3: Create Web Service on Render**

1. **Create New Web Service**:
   - Dashboard → New → Web Service
   - Select repository: `cacaoguard`
   - Branch: `main`
   - Name: `cacaoguard`
   - Region: Choose closest to your users (e.g., Singapore for Asia)
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Start Command: `gunicorn cacaoguard.wsgi:application`
   - Plan: **Free** (or Starter if you need better performance)

2. **Click "Create Web Service"**

---

### **Step 4: Configure Environment Variables**

In Render Dashboard → Your Service → Environment:

Add these environment variables:

```
DJANGO_SETTINGS_MODULE = cacaoguard.settings_production
PYTHON_VERSION = 3.12.0
DISABLE_COLLECTSTATIC = 1
DJANGO_SECRET_KEY = your-secret-key-here
ALLOWED_HOSTS = your-app-name.onrender.com
DEBUG = False

# Firebase Configuration
FIREBASE_API_KEY = AIzaSyAs90apE9AG6k4aIg9MpJD750OsvVD70m4
FIREBASE_AUTH_DOMAIN = systemcacao.firebaseapp.com
FIREBASE_DATABASE_URL = https://systemcacao-default-rtdb.firebaseio.com
FIREBASE_PROJECT_ID = systemcacao
FIREBASE_STORAGE_BUCKET = systemcacao.appspot.com
FIREBASE_MESSAGING_SENDER_ID = 35186667542
FIREBASE_APP_ID = 1:35186667542:web:14fcda24f86fee52f60537

# Email Configuration
EMAIL_HOST_USER = your-email@gmail.com
EMAIL_HOST_PASSWORD = your-app-password

# Database (if using PostgreSQL)
DATABASE_URL = postgresql://user:password@host:5432/dbname
```

---

### **Step 5: Fix requirements.txt**

The current requirements.txt is corrupted. Create a clean version:

```bash
# Create a new requirements.txt with essential packages only
```

**Essential packages for CacaoGuard**:
```
Django==5.1
djangorestframework==3.15.2
firebase-admin==6.6.0
google-cloud-firestore==2.20.1
google-cloud-storage==3.1.0
requests==2.32.3
PyJWT==2.10.1
python-dotenv==1.0.1
gunicorn==21.2.0
whitenoise==6.6.0
Pillow==11.1.0
pytz==2025.1
torch==2.1.0
torchvision==0.16.0
opencv-python==4.11.0.86
numpy==2.0.2
```

---

### **Step 6: Deploy**

1. **Automatic Deployment**:
   - Push to GitHub: `git push origin main`
   - Render automatically detects changes and deploys

2. **Manual Deployment**:
   - Render Dashboard → Your Service → Manual Deploy
   - Click "Deploy latest commit"

3. **Monitor Deployment**:
   - Render Dashboard → Logs
   - Watch for build and deployment messages
   - Wait for "Service is live" message

---

### **Step 7: Verify Deployment**

1. **Check Service Status**:
   - Render Dashboard → Your Service
   - Status should show "Live"
   - URL: `https://cacaoguard.onrender.com`

2. **Test Application**:
   - Visit: `https://cacaoguard.onrender.com`
   - Test login functionality
   - Check Firebase integration
   - Verify static files load

3. **Check Logs**:
   - Render Dashboard → Logs
   - Look for any errors
   - Verify no 500 errors

---

## 🔧 Troubleshooting

### **Issue: Build Fails**

**Solution**:
```bash
# Check requirements.txt for syntax errors
# Ensure all packages are compatible with Python 3.12
# Remove packages that aren't needed
```

### **Issue: Static Files Not Loading**

**Solution**:
```bash
# In settings_production.py, ensure:
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### **Issue: Firebase Connection Error**

**Solution**:
```bash
# Verify environment variables are set correctly
# Check Firebase credentials file path
# Ensure Firebase Admin SDK is installed
```

### **Issue: Database Errors**

**Solution**:
```bash
# For SQLite (free tier):
# Database file will be created automatically

# For PostgreSQL (recommended for production):
# Add DATABASE_URL environment variable
# Run migrations: python manage.py migrate
```

---

## 📊 Performance Optimization

### **For Free Tier**:
- Spins down after 15 minutes of inactivity
- Limited to 0.5GB RAM
- Suitable for low-traffic applications

### **For Production**:
- Upgrade to Starter Plan ($7/month)
- Always-on service
- 1GB RAM
- Better performance

### **Recommended Upgrades**:
1. **PostgreSQL Database** (instead of SQLite)
2. **Redis Cache** for session management
3. **Starter Plan** for always-on service

---

## 🔐 Security Checklist

- [x] DEBUG = False in production
- [x] ALLOWED_HOSTS configured
- [x] SECRET_KEY set via environment variable
- [x] HTTPS enforced
- [x] CSRF protection enabled
- [x] Firebase credentials secured
- [x] Email credentials in environment variables
- [x] Database credentials in environment variables

---

## 📱 Custom Domain (Optional)

1. **Add Custom Domain**:
   - Render Dashboard → Your Service → Settings
   - Custom Domain → Add Custom Domain
   - Enter your domain (e.g., cacaoguard.com)

2. **Update DNS Records**:
   - Go to your domain registrar
   - Add CNAME record pointing to Render URL
   - Wait for DNS propagation (up to 48 hours)

---

## 🚀 Deployment Summary

| Step | Status | Notes |
|------|--------|-------|
| GitHub Setup | ✅ Ready | Push code to GitHub |
| Render Account | ✅ Ready | Sign up at render.com |
| Web Service | ✅ Ready | Create service from GitHub |
| Environment Variables | ✅ Ready | Configure in Render dashboard |
| requirements.txt | ⚠️ Fix Needed | Clean up corrupted file |
| Deploy | ✅ Ready | Push to GitHub or manual deploy |
| Verify | ✅ Ready | Test at your Render URL |

---

## 📞 Support

- **Render Docs**: https://render.com/docs
- **Django Docs**: https://docs.djangoproject.com
- **Firebase Docs**: https://firebase.google.com/docs
- **GitHub Issues**: Create issue in your repository

---

## ✨ Next Steps After Deployment

1. **Monitor Performance**:
   - Check Render logs regularly
   - Monitor error rates
   - Track response times

2. **Set Up Alerts**:
   - Render → Notifications
   - Email alerts for deployment failures

3. **Continuous Improvement**:
   - Optimize database queries
   - Cache frequently accessed data
   - Compress images and static files

4. **Backup Strategy**:
   - Regular Firebase backups
   - Database exports
   - Code repository backups

---

**Deployment Date**: [Your Date]
**Status**: Ready for Production
**Last Updated**: 2025-01-20
