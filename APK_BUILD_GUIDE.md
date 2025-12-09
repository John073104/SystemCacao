# CacaoGuard APK Build Guide

## Method 1: WebView APK (Recommended - Easiest)

### Prerequisites
- Android Studio installed
- Your Django app deployed online (Render/Heroku)

### Steps

1. **Install Android Studio**
   ```
   Download: https://developer.android.com/studio
   Install with default settings
   ```

2. **Create New Project**
   - Open Android Studio
   - File → New → New Project
   - Select "Empty Activity"
   - Application name: CacaoGuard
   - Package name: com.systemcacao.cacaoguard
   - Language: Java
   - Minimum SDK: API 24 (Android 7.0)
   - Click Finish

3. **Modify AndroidManifest.xml**
   Location: `app/src/main/AndroidManifest.xml`
   
   Add permissions before `<application>`:
   ```xml
   <uses-permission android:name="android.permission.INTERNET" />
   <uses-permission android:name="android.permission.CAMERA" />
   <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
   <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
   <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
   ```

   Inside `<application>` add:
   ```xml
   android:usesCleartextTraffic="true"
   android:networkSecurityConfig="@xml/network_security_config"
   ```

4. **Create network_security_config.xml**
   Location: `app/src/main/res/xml/network_security_config.xml`
   ```xml
   <?xml version="1.0" encoding="utf-8"?>
   <network-security-config>
       <base-config cleartextTrafficPermitted="true">
           <trust-anchors>
               <certificates src="system" />
           </trust-anchors>
       </base-config>
   </network-security-config>
   ```

5. **Modify activity_main.xml**
   Location: `app/src/main/res/layout/activity_main.xml`
   ```xml
   <?xml version="1.0" encoding="utf-8"?>
   <RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
       android:layout_width="match_parent"
       android:layout_height="match_parent">

       <WebView
           android:id="@+id/webview"
           android:layout_width="match_parent"
           android:layout_height="match_parent" />
   </RelativeLayout>
   ```

6. **Modify MainActivity.java**
   Location: `app/src/main/java/com/systemcacao/cacaoguard/MainActivity.java`
   ```java
   package com.systemcacao.cacaoguard;

   import android.os.Bundle;
   import android.webkit.WebSettings;
   import android.webkit.WebView;
   import android.webkit.WebViewClient;
   import androidx.appcompat.app.AppCompatActivity;

   public class MainActivity extends AppCompatActivity {
       private WebView webView;

       @Override
       protected void onCreate(Bundle savedInstanceState) {
           super.onCreate(savedInstanceState);
           setContentView(R.layout.activity_main);

           webView = findViewById(R.id.webview);
           webView.setWebViewClient(new WebViewClient());
           
           WebSettings webSettings = webView.getSettings();
           webSettings.setJavaScriptEnabled(true);
           webSettings.setDomStorageEnabled(true);
           webSettings.setAllowFileAccess(true);
           webSettings.setAllowContentAccess(true);
           webSettings.setMediaPlaybackRequiresUserGesture(false);
           
           // Replace with your deployed URL
           webView.loadUrl("https://your-app.onrender.com");
       }

       @Override
       public void onBackPressed() {
           if (webView.canGoBack()) {
               webView.goBack();
           } else {
               super.onBackPressed();
           }
       }
   }
   ```

7. **Build APK**
   - Build → Build Bundle(s) / APK(s) → Build APK(s)
   - Wait for build to complete
   - Click "locate" to find APK file
   - APK location: `app/build/outputs/apk/debug/app-debug.apk`

8. **Test APK**
   - Transfer APK to Android phone
   - Enable "Install from Unknown Sources"
   - Install and test

---

## Method 2: Progressive Web App (PWA)

### Prerequisites
- Django app deployed with HTTPS
- manifest.json and service worker created

### Steps

1. **Add PWA files** (already created in /static/)
   - manifest.json
   - sw.js
   - icon-192.png
   - icon-512.png

2. **Update base template**
   Add to `<head>` in your base template:
   ```html
   <link rel="manifest" href="{% static 'manifest.json' %}">
   <meta name="theme-color" content="#10b981">
   <link rel="apple-touch-icon" href="{% static 'icon-192.png' %}">
   ```

   Add before `</body>`:
   ```html
   <script>
   if ('serviceWorker' in navigator) {
       navigator.serviceWorker.register('/static/sw.js');
   }
   </script>
   ```

3. **Create app icons**
   - Create 192x192 and 512x512 PNG icons
   - Save as icon-192.png and icon-512.png in /static/

4. **Deploy and test**
   - Deploy to production with HTTPS
   - Open in Chrome on Android
   - Click menu → "Install app" or "Add to Home Screen"

---

## Method 3: Using PWA Builder (No Code)

1. **Deploy your Django app** with HTTPS

2. **Visit PWABuilder.com**
   - Enter your deployed URL
   - Click "Start"

3. **Validate PWA**
   - Fix any issues reported
   - Ensure manifest.json is accessible

4. **Generate APK**
   - Click "Package for Stores"
   - Select Android
   - Download generated APK

5. **Test APK**
   - Install on Android device
   - Test all functionality

---

## Method 4: Using Capacitor (Advanced)

### Prerequisites
```powershell
npm install -g @capacitor/cli @capacitor/core
```

### Steps

1. **Initialize Capacitor**
   ```powershell
   cd C:\Users\ACER\Dropbox\PC\Downloads\cacaoguardbackup\cacaoguard
   npx cap init CacaoGuard com.systemcacao.app
   ```

2. **Add Android platform**
   ```powershell
   npx cap add android
   ```

3. **Configure capacitor.config.json**
   ```json
   {
     "appId": "com.systemcacao.app",
     "appName": "CacaoGuard",
     "webDir": "staticfiles",
     "server": {
       "url": "https://your-app.onrender.com",
       "cleartext": true
     }
   }
   ```

4. **Open in Android Studio**
   ```powershell
   npx cap open android
   ```

5. **Build APK in Android Studio**
   - Build → Build Bundle(s) / APK(s) → Build APK(s)

---

## Recommended Approach

**For your CacaoGuard app, I recommend Method 1 (WebView APK)** because:
- ✅ Easiest and fastest
- ✅ No code changes to Django required
- ✅ Works with your existing Render deployment
- ✅ Camera and file upload work with proper permissions
- ✅ Can update app content without rebuilding APK

## Important Notes

1. **Your Django app must be deployed online** (Render, Heroku, etc.)
2. **Use HTTPS** for production
3. **Test all features** on Android device (camera, file upload, Firebase auth)
4. **For Google Play Store**, you need:
   - Signed APK (not debug APK)
   - Developer account ($25 one-time fee)
   - Privacy policy
   - App screenshots and description

Would you like me to help you with any specific method?
