# CacaoGuard Deployment Guide for Render

## Prerequisites
- GitHub repository with your code
- Render account
- Firebase project with service account key

## Deployment Steps

### 1. Prepare Your Repository
- Ensure all dependencies are in `requirements.txt`
- Create `render.yaml` and `Procfile` (already created)
- Make sure your Django settings are production-ready

### 2. Deploy to Render

#### Option A: Using Render Dashboard
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: cacaoguard
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command**: `gunicorn cacaoguard.wsgi:application`
   - **Plan**: Free (or upgrade as needed)

#### Option B: Using render.yaml (Recommended)
1. Push your code to GitHub
2. In Render dashboard, click "New +" → "Blueprint"
3. Connect your repository
4. Render will automatically detect and use the `render.yaml` configuration

### 3. Environment Variables
Set these in your Render service settings:

```
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-render-app-url.onrender.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 4. Firebase Configuration
1. Upload your Firebase service account key to Render
2. Set the environment variable:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=/opt/render/project/src/mainapp/systemcacao-firebase-adminsdk-fbsvc-126c1bf0e1.json
   ```

### 5. Static Files Storage
For production, consider using:
- **AWS S3** for static files
- **Cloudinary** for media files
- **Firebase Storage** for user uploads

### 6. Database
- SQLite is fine for small applications
- For production with multiple users, consider PostgreSQL
- Render provides managed PostgreSQL databases

### 7. Monitoring
- Enable Render's built-in monitoring
- Set up error tracking (Sentry)
- Monitor Firebase usage and costs

## Post-Deployment Checklist
- [ ] Test all functionality
- [ ] Verify Firebase integration
- [ ] Check static files are served correctly
- [ ] Test user registration and login
- [ ] Verify email functionality
- [ ] Test file uploads
- [ ] Monitor performance

## Troubleshooting
- Check Render logs for errors
- Verify environment variables are set
- Ensure Firebase credentials are correct
- Check static files configuration
- Monitor database migrations

## Cost Optimization
- Use Render's free tier for development
- Optimize static files (compress images)
- Implement caching strategies
- Monitor Firebase usage
- Use CDN for static assets
