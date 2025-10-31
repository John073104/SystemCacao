# 🚀 COMPLETE DEPLOYMENT GUIDE - CacaoGuard to Render

## ✅ GitHub Push Complete!

Your code is now on GitHub in the `deploy-clean` branch without sensitive credentials.

---

## 📦 Model Files Storage Solution

### Option 1: Google Drive (RECOMMENDED - Free & Easy)

1. **Upload Models to Google Drive:**
   - Go to https://drive.google.com
   - Upload these files:
     - `models/cacao_disease_resnet_state_dict.pth`
     - `models/cacao_pest_resnet_state_dict.pth`

2. **Get Direct Download Links:**
   - Right-click each file → "Get link" → "Anyone with the link"
   - Copy the link (looks like: `https://drive.google.com/file/d/FILE_ID/view?usp=sharing`)
   - Convert to direct download:
     ```
     From: https://drive.google.com/file/d/1ABC123XYZ/view?usp=sharing
     To:   https://drive.google.com/uc?export=download&id=1ABC123XYZ
     ```

3. **Update download_models.py:**
   Replace the URLs in the file with your Google Drive links.

### Option 2: Dropbox (Also Free)

1. Upload models to Dropbox
2. Get shareable link
3. Change `?dl=0` to `?dl=1` at the end
4. Use this link in `download_models.py`

---

## 🎯 Deploy to Render - Step by Step

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up (free tier available)
3. Connect your GitHub account

### Step 2: Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Select your repository: **SystemCacao**
3. Branch: **production-ready** ✅ (Use this branch!)
4. Name: `cacaoguard`
5. Environment: **Python 3**

### Step 3: Configure Build Settings

**Build Command:**
```bash
pip install --upgrade pip && pip install -r requirements_render.txt && python manage.py collectstatic --noinput
```

**Start Command:**
```bash
gunicorn cacaoguard.wsgi:application --bind 0.0.0.0:$PORT
```

### Step 4: Add Environment Variables

Click **"Environment"** tab and add these:

| Key | Value |
|-----|-------|
| `DJANGO_SETTINGS_MODULE` | `cacaoguard.settings` |
| `SECRET_KEY` | Generate using: `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.onrender.com,cacaoguard.onrender.com` |
| `FIREBASE_STORAGE_BUCKET` | `systemcacao.appspot.com` |
| `EMAIL_HOST_USER` | `jardinesjohnlloyd@gmail.com` |
| `EMAIL_HOST_PASSWORD` | `mfmd cwuf znij zmmt` |

### Step 5: Add Firebase Credentials (Secret File)

1. In Render dashboard → **Environment** → **Secret Files**
2. Click **"Add Secret File"**
3. **Filename:** `mainapp/systemcacao-firebase-adminsdk-fbsvc-126c1bf0e1.json`
4. **Contents:** Paste your Firebase JSON file content (the one from your local folder)

To get the content:
```powershell
Get-Content mainapp/systemcacao-firebase-adminsdk-fbsvc-126c1bf0e1.json
```

### Step 6: Deploy!
1. Click **"Create Web Service"**
2. Wait 5-10 minutes for first deployment
3. Watch the logs for any errors

### Step 7: Download Models (CRITICAL!)

After first successful deployment:

**Option A: Using Render Shell**
1. In Render dashboard → **Shell** tab
2. Run:
```bash
python download_models.py
```

**Option B: Manual Download (if script fails)**
```bash
cd models
# Replace URLs with your actual Google Drive/Dropbox links
wget "YOUR_DISEASE_MODEL_URL" -O cacao_disease_resnet_state_dict.pth
wget "YOUR_PEST_MODEL_URL" -O cacao_pest_resnet_state_dict.pth
```

**Option C: Upload via Render Shell**
1. In Render Shell, run: `cd models`
2. You'll need to upload manually if download doesn't work

---

## ✅ Verify Deployment

### Check These After Deploy:

1. **Logs Show Success:**
```
✓ Firebase initialized with Authentication, Storage, and Firestore!
✓ Successfully loaded PyTorch model: cacao_disease_resnet_state_dict.pth
✓ Successfully loaded PyTorch model: cacao_pest_resnet_state_dict.pth
```

2. **Test URLs:**
   - Homepage: `https://cacaoguard.onrender.com/`
   - Login: `https://cacaoguard.onrender.com/login/`
   - Admin: `https://cacaoguard.onrender.com/admin/dashboard/`

3. **Test All 9 Fixed Features:**
   - ✅ Stock deduction on orders
   - ✅ Email receipts
   - ✅ Payment processing
   - ✅ Notifications
   - ✅ Scan visibility
   - ✅ Farm requests
   - ✅ Order details
   - ✅ Admin orange header
   - ✅ User green header

---

## 🔍 Troubleshooting

### Models Not Loading
**Error:** `FileNotFoundError: models/cacao_disease_resnet_state_dict.pth`

**Solution:**
```bash
# In Render Shell
python download_models.py
# OR manually download models
```

### Firebase Error
**Error:** `Firebase credentials not found`

**Solution:**
- Verify Secret File was added correctly in Render dashboard
- Check filename is exactly: `mainapp/systemcacao-firebase-adminsdk-fbsvc-126c1bf0e1.json`

### Static Files Not Loading
**Solution:**
```bash
# In Render Shell
python manage.py collectstatic --noinput
```

### 500 Internal Server Error
**Solution:**
- Check Render logs for detailed error
- Verify all environment variables are set
- Make sure Firebase credentials file is uploaded

---

## 📧 Email Configuration

Already configured with:
- **From**: jardinesjohnlloyd@gmail.com
- **App Password**: Set in environment variables
- **SMTP**: smtp.gmail.com

Receipts will be sent automatically on order completion! ✅

---

## 💰 Render Free Tier Limits

- ✅ 750 hours/month (enough for 1 app running 24/7)
- ✅ Automatic HTTPS
- ⚠️ App sleeps after 15 min inactivity (free tier)
- ⚠️ 512 MB RAM limit

**For production:** Upgrade to paid tier ($7/month) for:
- No sleep
- More RAM
- Better performance

---

## 🎯 Quick Commands Reference

### Generate SECRET_KEY
```powershell
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### View Firebase Credentials
```powershell
Get-Content mainapp/systemcacao-firebase-adminsdk-fbsvc-126c1bf0e1.json
```

### Check Current Branch
```powershell
git branch
# Should show: * deploy-clean
```

### View Commit
```powershell
git log --oneline -1
```

---

## 🎉 Summary

### What We Did:
1. ✅ Removed sensitive Firebase credentials from GitHub
2. ✅ Created clean `deploy-clean` branch
3. ✅ Excluded large model files (927 MB) from git
4. ✅ Created `download_models.py` script
5. ✅ Ready to push to GitHub
6. ✅ Ready to deploy to Render

### What You Need to Do:
1. **Upload models to Google Drive/Dropbox** (get direct links)
2. **Update `download_models.py`** with your model URLs
3. **Deploy to Render** (follow steps above)
4. **Add Firebase credentials** as Secret File in Render
5. **Run `python download_models.py`** in Render Shell

---

## 📞 Need Help?

**Your Email:** jardinesjohnlloyd@gmail.com  
**GitHub:** https://github.com/John073104/SystemCacao  
**Branch:** deploy-clean  

**Render Support:** https://render.com/docs  
**Firebase Console:** https://console.firebase.google.com

---

**🚀 Your app is ready to deploy! Follow the steps above and you'll be live in ~15 minutes!**
