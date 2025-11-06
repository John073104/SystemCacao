# Add Cloudinary Environment Variables to Render

## Step-by-Step Instructions:

### 1. Go to Render Dashboard
Open: https://dashboard.render.com/

### 2. Select Your Web Service
- Click on your `cacaoguard` or `SystemCacao` web service

### 3. Go to Environment Tab
- On the left sidebar, click **Environment**

### 4. Add Environment Variables
Click **Add Environment Variable** button and add these THREE variables:

**Variable 1:**
```
Key: CLOUDINARY_CLOUD_NAME
Value: driikw8gl
```

**Variable 2:**
```
Key: CLOUDINARY_API_KEY
Value: 234447251498868
```

**Variable 3:**
```
Key: CLOUDINARY_API_SECRET
Value: vnAHNsYf1saLaSGU7X8sQpQY4d4
```

### 5. Save Changes
- Click **Save Changes** button at the bottom
- Render will automatically redeploy your service

### 6. Wait for Deployment
- Watch the deployment logs
- Wait until it says "Live" (usually 2-5 minutes)

### 7. Test
- Go to your admin panel
- Add a new product with an image
- Check marketplace - the image should appear!

---

## ✅ Verification Checklist:
- [ ] All 3 environment variables added
- [ ] Deployment successful (status shows "Live")
- [ ] Can add new product with image in admin
- [ ] New product image shows in marketplace
