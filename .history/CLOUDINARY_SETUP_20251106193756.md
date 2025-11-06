# Cloudinary Setup for Product Images

## Why Cloudinary?
- ✅ **FREE** 25GB storage + 25GB bandwidth/month
- ✅ Images persist across Render deploys
- ✅ Auto image optimization
- ✅ CDN delivery (fast worldwide)

## Setup Steps:

### 1. Create FREE Cloudinary Account
1. Go to: https://cloudinary.com/users/register_free
2. Sign up with email
3. Verify your email

### 2. Get Your API Credentials
1. Login to Cloudinary Dashboard: https://console.cloudinary.com/
2. You'll see your credentials:
   - **Cloud Name**: (e.g., "dxxxxxxxx")
   - **API Key**: (e.g., "123456789012345")
   - **API Secret**: (e.g., "abcdefghijklmnopqrstuvwxyz123")

### 3. Add to Render Environment Variables
1. Go to your Render dashboard: https://dashboard.render.com/
2. Select your web service
3. Go to **Environment** tab
4. Add these variables:
   ```
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   ```
5. Click **Save Changes**

### 4. Test Locally (Optional)
Create `.env` file in project root:
```
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### 5. Redeploy on Render
- Push changes to GitHub
- Render will auto-deploy
- Now when admin uploads product images, they go to Cloudinary!

## How It Works:
1. **Admin uploads image** → Uploaded to Cloudinary
2. **Cloudinary returns URL** → Saved in Firestore
3. **User views marketplace** → Images loaded from Cloudinary CDN
4. **Images persist forever** → No more 404 errors!

## Check Your Images:
After uploading products, check Cloudinary dashboard:
- Media Library → cacaoguard/products folder
- You'll see all uploaded product images

## Free Tier Limits:
- Storage: 25GB
- Bandwidth: 25GB/month
- Transformations: 25,000/month
- More than enough for your app!
