# 🆓 NEW RENDER ACCOUNT SETUP GUIDE
## Deploy CacaoGuard with Fresh Free Minutes - November 2025

---

## STEP 1: CREATE NEW RENDER ACCOUNT

### 1.1 Logout from Current Account
- Go to: https://dashboard.render.com
- Click your profile (top right)
- Click "Sign Out"

### 1.2 Create New Account
- Go to: https://render.com
- Click **"Get Started"** or **"Sign Up"**
- Use a **DIFFERENT email** than your current account
  
**Email Options:**
- Use alternate email (Gmail, Yahoo, etc.)
- Or use Gmail alias: `youremail+render2@gmail.com`
- Or use a friend's email temporarily

### 1.3 Verify Email
- Check inbox for Render verification email
- Click verification link
- Login to new account

---

## STEP 2: CONNECT GITHUB REPOSITORY

### 2.1 Create New Web Service
- In Render Dashboard, click **"New +"** (top right)
- Select **"Web Service"**

### 2.2 Connect GitHub
- Click **"Connect GitHub"**
- If prompted, authorize Render to access GitHub
- You'll see a list of your repositories

### 2.3 Select Repository
- Find: **"SystemCacao"**
- Click **"Connect"**

---

## STEP 3: CONFIGURE SERVICE

### 3.1 Basic Settings
Fill in these EXACT values:

**Name:** `cacaoguard-nov2025`

**Region:** `Singapore` (or closest to you)

**Branch:** `production-ready`

**Root Directory:** (leave BLANK)

**Runtime:** `Python 3`

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
gunicorn cacaoguard.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

### 3.2 Instance Type
- Select: **Free** (0.1 CPU, 512 MB RAM)

---

## STEP 4: ADD ENVIRONMENT VARIABLES

Click **"Advanced"** → Scroll to **"Environment Variables"**

Add these ONE BY ONE:

### Required Variables:

**1. CLOUDINARY_CLOUD_NAME**
```
driikw8gl
```

**2. CLOUDINARY_API_KEY**
```
234447251498868
```

**3. CLOUDINARY_API_SECRET**
```
<YOU NEED TO FIND THIS IN YOUR OLD RENDER SERVICE>
```

**To get CLOUDINARY_API_SECRET from old service:**
1. Open old Render account in new tab (login with original email)
2. Go to: https://dashboard.render.com/web/cacaoguard2
3. Click "Environment" tab
4. Find CLOUDINARY_API_SECRET
5. Copy the value
6. Paste it in new service

**4. CLOUDINARY_URL**
```
cloudinary://234447251498868:<SAME_SECRET_AS_ABOVE>@driikw8gl
```
(Replace `<SAME_SECRET_AS_ABOVE>` with the actual secret)

**5. DJANGO_SETTINGS_MODULE**
```
cacaoguard.settings
```

**6. PYTHON_VERSION**
```
3.11.0
```

---

## STEP 5: ADD FIREBASE CREDENTIALS (SECRET FILE)

### 5.1 Scroll to "Secret Files" Section
Click **"Add Secret File"**

### 5.2 Configure Secret File

**Filename:**
```
systemcacao-firebase-adminsdk-fbsvc-126c1bf0e1.json
```

**Contents:**
Open your local file:
```
C:\Users\ACER\Dropbox\PC\Downloads\cacaoguardbackup\cacaoguard\mainapp\systemcacao-firebase-adminsdk-fbsvc-126c1bf0e1.json
```

Copy the ENTIRE contents and paste into Render's text box.

---

## STEP 6: CREATE AND DEPLOY

### 6.1 Review Settings
- Double-check all environment variables
- Verify secret file is added
- Confirm start command is correct

### 6.2 Click "Create Web Service"
- Render will start building immediately
- This will take 3-5 minutes

### 6.3 Watch Build Logs
- You'll see live logs on screen
- Wait for: **"Your service is live 🎉"**

---

## STEP 7: GET YOUR NEW URL

After deployment completes:

**Your NEW site URL will be:**
```
https://cacaoguard-nov2025.onrender.com
```

(Or whatever name you chose instead of "cacaoguard-nov2025")

---

## STEP 8: TEST YOUR NEW SITE

### 8.1 Test Marketplace
Visit: `https://cacaoguard-nov2025.onrender.com/guest/marketplace/`

**Check:**
- ✅ All 10 products show real images
- ✅ Products load properly

### 8.2 Test Checkout with GCash
1. Login with test account
2. Add item to cart
3. Go to checkout
4. Choose **"GCash"** payment
5. Complete order

**You should see:**
- ✅ GCash Number: 09123456789
- ✅ Account Name: CacaoGuard Marketplace
- ✅ Step-by-step payment instructions
- ✅ Amount to pay

### 8.3 Test Order Confirmation
- Order confirmation page should load without errors
- GCash instructions should be visible

---

## TROUBLESHOOTING

### Build Fails?
**Check:**
1. Branch is set to `production-ready`
2. All environment variables spelled correctly
3. Secret file uploaded with correct filename

### Site Shows Error?
**Check:**
1. Firebase secret file contents are complete JSON
2. CLOUDINARY_API_SECRET is correct
3. Wait 2-3 minutes after "live" message for full startup

### Images Not Showing?
**They should work immediately because:**
- Images are on Cloudinary (already uploaded)
- Database has Cloudinary URLs (already updated)
- No re-upload needed!

---

## WHAT ABOUT OLD SITE?

### Old Site Status:
- ❌ URL: `https://cacaoguard2.onrender.com`
- ❌ No GCash payment instructions (not deployed)
- ✅ Still has marketplace images (database update)
- ✅ Still functional for basic operations

### New Site Status:
- ✅ URL: `https://cacaoguard-nov2025.onrender.com`
- ✅ Has GCash payment instructions
- ✅ Has marketplace images
- ✅ Fully functional with all fixes

### Both Sites Share:
- ✅ Same Firebase database (all orders, users)
- ✅ Same Cloudinary images
- ✅ Same product data

You can keep both running or delete the old one later!

---

## CHECKLIST

Before clicking "Create Web Service":

- [ ] Name: cacaoguard-nov2025 (or your choice)
- [ ] Region: Singapore
- [ ] Branch: production-ready
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `gunicorn cacaoguard.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
- [ ] CLOUDINARY_CLOUD_NAME added
- [ ] CLOUDINARY_API_KEY added
- [ ] CLOUDINARY_API_SECRET added (from old service)
- [ ] CLOUDINARY_URL added (with secret)
- [ ] DJANGO_SETTINGS_MODULE added
- [ ] PYTHON_VERSION added
- [ ] Firebase JSON file uploaded as secret file

---

## READY TO START?

1. Open new incognito/private browser window
2. Go to: https://render.com
3. Follow steps above
4. Come back here if you need help!

**TOTAL TIME: 10-15 minutes**
**COST: $0 (FREE)**
**RESULT: Fully working site with GCash instructions!**

---

## NEED HELP?

If you get stuck at any step, tell me:
1. Which step number?
2. What error or issue?
3. Screenshot if possible

I'll help you fix it immediately!
