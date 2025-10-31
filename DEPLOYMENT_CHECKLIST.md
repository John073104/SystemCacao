# ✅ CacaoGuard Render Deployment Checklist

## 🔍 Pre-Deployment Verification

### Code Quality
- [ ] All duplicate functions removed (especially `userdashboard`)
- [ ] No syntax errors in Python files
- [ ] No console errors in JavaScript
- [ ] All imports are correct
- [ ] No hardcoded credentials in code

### Configuration Files
- [ ] `render.yaml` exists and is correct
- [ ] `Procfile` exists
- [ ] `requirements_clean.txt` is valid
- [ ] `settings_production.py` is configured
- [ ] `.gitignore` excludes sensitive files

### Firebase Setup
- [ ] Firebase project created (systemcacao)
- [ ] Firebase Admin SDK credentials downloaded
- [ ] Firestore database initialized
- [ ] Firebase Storage bucket created
- [ ] Firebase Authentication enabled

### Static Files
- [ ] All CSS files in `static/css/`
- [ ] All JavaScript files in `static/js/`
- [ ] All images in `static/images/`
- [ ] `STATIC_ROOT` configured in settings
- [ ] `STATIC_URL` set to `/static/`

### Templates
- [ ] All HTML templates in `templates/` directory
- [ ] `{% load static %}` tag in all templates
- [ ] No broken template tags
- [ ] All template variables passed from views

### Database
- [ ] Migrations created: `python manage.py makemigrations`
- [ ] Migrations applied: `python manage.py migrate`
- [ ] No pending migrations

---

## 🔐 Security Checklist

### Django Settings
- [ ] `DEBUG = False` in production
- [ ] `ALLOWED_HOSTS` configured with your domain
- [ ] `SECRET_KEY` set via environment variable
- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`

### Credentials
- [ ] No API keys in code
- [ ] No passwords in code
- [ ] No Firebase credentials in code
- [ ] All secrets in environment variables
- [ ] `.env` file in `.gitignore`

### HTTPS
- [ ] SSL certificate configured
- [ ] HTTPS enforced
- [ ] Mixed content warnings resolved

---

## 📦 GitHub Setup

### Repository
- [ ] GitHub account created
- [ ] Repository created: `cacaoguard`
- [ ] Repository is public (for free Render tier)
- [ ] `.gitignore` configured properly

### Git Configuration
```bash
# Initialize repository
git init
git add .
git commit -m "Initial commit - CacaoGuard ready for deployment"

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/cacaoguard.git
git branch -M main
git push -u origin main
```

- [ ] Repository initialized
- [ ] All files committed
- [ ] Pushed to GitHub main branch
- [ ] No sensitive files in repository

---

## 🚀 Render Setup

### Account & Service
- [ ] Render account created
- [ ] GitHub connected to Render
- [ ] Web Service created
- [ ] Service name: `cacaoguard`
- [ ] Runtime: Python 3
- [ ] Region: Selected (Singapore recommended for Asia)

### Build & Start Commands
- [ ] Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- [ ] Start Command: `gunicorn cacaoguard.wsgi:application`
- [ ] Plan: Free (or Starter for production)

### Environment Variables
```
DJANGO_SETTINGS_MODULE = cacaoguard.settings_production
PYTHON_VERSION = 3.12.0
DISABLE_COLLECTSTATIC = 1
DJANGO_SECRET_KEY = [generate-new-key]
ALLOWED_HOSTS = cacaoguard.onrender.com
DEBUG = False

# Firebase
FIREBASE_API_KEY = AIzaSyAs90apE9AG6k4aIg9MpJD750OsvVD70m4
FIREBASE_AUTH_DOMAIN = systemcacao.firebaseapp.com
FIREBASE_DATABASE_URL = https://systemcacao-default-rtdb.firebaseio.com
FIREBASE_PROJECT_ID = systemcacao
FIREBASE_STORAGE_BUCKET = systemcacao.appspot.com
FIREBASE_MESSAGING_SENDER_ID = 35186667542
FIREBASE_APP_ID = 1:35186667542:web:14fcda24f86fee52f60537

# Email
EMAIL_HOST_USER = your-email@gmail.com
EMAIL_HOST_PASSWORD = your-app-password
```

- [ ] All environment variables added
- [ ] No typos in variable names
- [ ] Sensitive values are secure

---

## ✅ Pre-Deployment Testing

### Local Testing
```bash
# Test production settings locally
export DJANGO_SETTINGS_MODULE=cacaoguard.settings_production
python manage.py runserver

# Test static files collection
python manage.py collectstatic --noinput

# Test migrations
python manage.py migrate

# Run tests
python manage.py test
```

- [ ] Application runs locally with production settings
- [ ] Static files collect without errors
- [ ] Migrations apply successfully
- [ ] No 500 errors on main pages
- [ ] Login functionality works
- [ ] Firebase integration works

### Functionality Testing
- [ ] Home page loads
- [ ] Login page loads
- [ ] Signup page loads
- [ ] Dashboard loads (after login)
- [ ] Static files load (CSS, JS, images)
- [ ] Firebase authentication works
- [ ] Firestore queries work
- [ ] File uploads work

---

## 🚀 Deployment Steps

### Step 1: Final Code Push
```bash
git add .
git commit -m "Final deployment preparation"
git push origin main
```
- [ ] Code pushed to GitHub

### Step 2: Monitor Deployment
- [ ] Render detects new push
- [ ] Build starts automatically
- [ ] Build completes successfully
- [ ] Service deploys
- [ ] Service shows "Live" status

### Step 3: Verify Deployment
- [ ] Visit: `https://cacaoguard.onrender.com`
- [ ] Home page loads
- [ ] No 500 errors
- [ ] Static files load
- [ ] Login works
- [ ] Firebase integration works

---

## 🔍 Post-Deployment Verification

### Application Functionality
- [ ] Home page accessible
- [ ] Login page accessible
- [ ] Signup page accessible
- [ ] User can register
- [ ] User can login
- [ ] User dashboard loads
- [ ] Admin dashboard loads (if admin)
- [ ] Scan functionality works
- [ ] Marketplace loads
- [ ] Farm mapping loads
- [ ] Orders work
- [ ] Checkout works

### Performance
- [ ] Page load time < 3 seconds
- [ ] No console errors
- [ ] No network errors
- [ ] Images load properly
- [ ] Charts render correctly

### Monitoring
- [ ] Check Render logs for errors
- [ ] Monitor error rate
- [ ] Check response times
- [ ] Verify no 500 errors
- [ ] Check Firebase quota usage

---

## 🐛 Troubleshooting

### Build Fails
- [ ] Check `requirements.txt` syntax
- [ ] Verify all packages are compatible
- [ ] Check Python version compatibility
- [ ] Review build logs in Render

### Application Won't Start
- [ ] Check `DJANGO_SETTINGS_MODULE` environment variable
- [ ] Verify `settings_production.py` exists
- [ ] Check for syntax errors in settings
- [ ] Review start command in Render

### Static Files Not Loading
- [ ] Verify `STATIC_ROOT` is set
- [ ] Check `STATIC_URL` is correct
- [ ] Run `collectstatic` locally to test
- [ ] Check WhiteNoise middleware is installed

### Firebase Connection Error
- [ ] Verify Firebase credentials
- [ ] Check environment variables
- [ ] Verify Firebase project ID
- [ ] Check Firestore database exists

### Database Errors
- [ ] Run migrations: `python manage.py migrate`
- [ ] Check database URL in environment
- [ ] Verify database credentials
- [ ] Check database is accessible

---

## 📊 Deployment Status

| Component | Status | Notes |
|-----------|--------|-------|
| Code | ✅ Ready | All files prepared |
| Configuration | ✅ Ready | render.yaml, Procfile, settings |
| Firebase | ✅ Ready | Credentials configured |
| GitHub | ⏳ Pending | Push code to GitHub |
| Render | ⏳ Pending | Create service on Render |
| Environment Variables | ⏳ Pending | Add to Render dashboard |
| Deployment | ⏳ Pending | Push to GitHub to trigger |
| Verification | ⏳ Pending | Test after deployment |

---

## 📞 Support Resources

- **Render Documentation**: https://render.com/docs
- **Django Documentation**: https://docs.djangoproject.com
- **Firebase Documentation**: https://firebase.google.com/docs
- **GitHub Help**: https://docs.github.com

---

## 🎯 Next Steps

1. **Immediate** (Before Deployment):
   - [ ] Fix requirements.txt
   - [ ] Remove duplicate functions
   - [ ] Test locally with production settings
   - [ ] Push to GitHub

2. **Deployment** (Day 1):
   - [ ] Create Render account
   - [ ] Connect GitHub
   - [ ] Create Web Service
   - [ ] Add environment variables
   - [ ] Monitor deployment

3. **Post-Deployment** (Day 2+):
   - [ ] Verify all functionality
   - [ ] Monitor logs
   - [ ] Set up alerts
   - [ ] Plan optimizations

---

**Prepared By**: CacaoGuard Team
**Date**: 2025-01-20
**Status**: Ready for Deployment
**Estimated Deployment Time**: 10-15 minutes
