# 🚀 RENDER DEPLOYMENT GUIDE - CacaoGuard

## 📋 Pre-Deployment Checklist

### 1. Clean Git Status
```bash
git status
git add .
git commit -m "Production ready for Render deployment"
```

### 2. Force Push to GitHub (if needed)
```bash
git push -f origin main
```

## 🔧 Render Setup Steps

### Step 1: Create New Web Service
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `John073104/SystemCacao`
4. Select branch: `main`

### Step 2: Configure Service
- **Name**: `cacaoguard`
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Build Command**: 
  ```bash
  pip install -r requirements.txt && python manage.py collectstatic --noinput
  ```
- **Start Command**: 
  ```bash
  gunicorn cacaoguard.wsgi:application
  ```

### Step 3: Environment Variables
Add these in Render dashboard under "Environment":

```
DJANGO_SETTINGS_MODULE=cacaoguard.settings_production
SECRET_KEY=<generate-a-strong-random-key>
DEBUG=False
ALLOWED_HOSTS=.render.com,cacaoguard.onrender.com
DATABASE_URL=<your-postgres-url-if-using-postgres>
FIREBASE_STORAGE_BUCKET=systemcacao.appspot.com
```

**To generate SECRET_KEY:**
```python
import secrets
print(secrets.token_urlsafe(50))
```

### Step 4: Add Firebase Credentials
In Render dashboard:
1. Go to **Environment**
2. Add **Secret File**:
   - **Filename**: `mainapp/systemcacao-firebase-adminsdk-fbsvc-126c1bf0e1.json`
   - **Contents**: Paste your Firebase service account JSON

### Step 5: Download Model Files (CRITICAL)
After first deployment:
1. Open Render Shell (Dashboard → Shell tab)
2. Upload model files or run:
   ```bash
   # Option A: If you uploaded models to cloud storage
   python download_models.py
   
   # Option B: Manual download (example with wget)
   cd models
   wget "YOUR_DISEASE_MODEL_URL" -O cacao_disease_resnet_state_dict.pth
   wget "YOUR_PEST_MODEL_URL" -O cacao_pest_resnet_state_dict.pth
   ```

### Step 6: Deploy!
1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Access your app at: `https://cacaoguard.onrender.com`

## 🔍 Post-Deployment Verification

### Check Logs
```bash
# In Render dashboard, go to Logs tab
# Look for:
✓ Firebase initialized with Authentication, Storage, and Firestore!
✓ Successfully loaded PyTorch model: models/cacao_disease_resnet_state_dict.pth
✓ Successfully loaded PyTorch model: models/cacao_pest_resnet_state_dict.pth
```

### Test Endpoints
1. **Homepage**: `https://cacaoguard.onrender.com/`
2. **Login**: `https://cacaoguard.onrender.com/login/`
3. **Admin**: `https://cacaoguard.onrender.com/admin/dashboard/`

## 🐛 Troubleshooting

### Issue: Models Not Loading
**Solution**: Run `python download_models.py` in Render Shell

### Issue: Firebase Errors
**Solution**: Verify Firebase credentials file is uploaded correctly

### Issue: Static Files Not Loading
**Solution**: Run in Render Shell:
```bash
python manage.py collectstatic --noinput
```

### Issue: 500 Internal Server Error
**Solution**: Check logs in Render dashboard for detailed error

## 📦 Model File Storage Options

### Option 1: Google Drive (Free)
1. Upload models to Google Drive
2. Right-click → Get shareable link
3. Convert to direct download link:
   ```
   https://drive.google.com/file/d/FILE_ID/view?usp=sharing
   →
   https://drive.google.com/uc?export=download&id=FILE_ID
   ```

### Option 2: Dropbox (Free)
1. Upload to Dropbox
2. Get share link, change `?dl=0` to `?dl=1`

### Option 3: AWS S3 / Google Cloud Storage (Recommended for production)

## 🔐 Security Notes

- ✅ Firebase credentials are in Secret Files (not in code)
- ✅ DEBUG=False in production
- ✅ SECRET_KEY is environment variable
- ✅ ALLOWED_HOSTS is restricted
- ⚠️ Model files are NOT in git (download separately)

## 📧 Email Configuration

Email is already configured with:
- **Email**: jardinesjohnlloyd@gmail.com
- **Password**: App-specific password set

## 🎉 Success Indicators

When deployment is successful, you should see:
- ✓ Green "Live" status in Render dashboard
- ✓ No errors in logs
- ✓ All pages load correctly
- ✓ Image scanning works
- ✓ Notifications appear
- ✓ Payment integration ready

## 💡 Next Steps After Deployment

1. **Test all 9 fixed features**:
   - Stock deduction on orders
   - Email receipts
   - Payment processing
   - Notification system
   - Scan visibility toggle
   - Farm request approval
   - Order details loading
   - Admin orange gradient
   - User green gradient

2. **Set up monitoring**:
   - Enable Render health checks
   - Monitor resource usage

3. **Custom domain** (optional):
   - Add your custom domain in Render settings

---

**Need Help?** Check Render documentation: https://render.com/docs
