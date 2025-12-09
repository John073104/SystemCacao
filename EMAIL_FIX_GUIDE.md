# Email Configuration Fix Guide - CacaoGuard

## 🔧 Steps to Fix Email Not Working

### Option 1: Update Gmail App Password (RECOMMENDED)

1. **Go to Google Account Settings:**
   - Visit: https://myaccount.google.com/
   - Login with: `jardinesjohnlloyd@gmail.com`

2. **Enable 2-Factor Authentication:**
   - Go to Security → 2-Step Verification
   - Turn ON if not already enabled
   - Follow the setup wizard

3. **Generate New App Password:**
   - Go to Security → 2-Step Verification → App passwords
   - Select app: "Mail"
   - Select device: "Windows Computer"
   - Click "Generate"
   - **Copy the 16-character password** (e.g., "abcd efgh ijkl mnop")

4. **Update settings.py:**
   ```python
   EMAIL_HOST_PASSWORD = 'your-new-app-password-here'  # Replace with new password (no spaces)
   ```

5. **Restart Django server**

---

### Option 2: Use SendGrid (FREE & RELIABLE)

SendGrid offers 100 free emails/day - much more reliable than Gmail.

1. **Sign up for SendGrid:**
   - Visit: https://signup.sendgrid.com/
   - Create free account

2. **Get API Key:**
   - Go to Settings → API Keys
   - Create API Key
   - Copy the key (starts with "SG.")

3. **Install SendGrid:**
   ```powershell
   .venv\Scripts\Activate
   pip install sendgrid
   ```

4. **Update settings.py:**
   ```python
   # Replace existing EMAIL_* settings with:
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = 'smtp.sendgrid.net'
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = 'apikey'  # This is literally "apikey"
   EMAIL_HOST_PASSWORD = 'SG.your-api-key-here'  # Your actual SendGrid API key
   DEFAULT_FROM_EMAIL = 'jardinesjohnlloyd@gmail.com'  # Must be verified in SendGrid
   ```

5. **Verify Sender Email in SendGrid:**
   - Go to Settings → Sender Authentication
   - Verify Single Sender: `jardinesjohnlloyd@gmail.com`
   - Check your email and click verification link

---

### Option 3: Use Console Backend (TESTING ONLY)

For testing without actual email sending:

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

This will print emails to the console instead of sending them.

---

## 🧪 Test Email Functionality

After fixing, test with Python shell:

```powershell
cd C:\Users\ACER\Dropbox\PC\Downloads\cacaoguardbackup\cacaoguard
.venv\Scripts\Activate
python manage.py shell
```

```python
from django.core.mail import send_mail

# Test email
send_mail(
    'Test Email from CacaoGuard',
    'If you receive this, email is working!',
    'jardinesjohnlloyd@gmail.com',
    ['your-test-email@example.com'],
    fail_silently=False,
)
```

If no errors appear → Email is working! ✅

---

## 📋 Common Error Messages

### Error: "SMTPAuthenticationError"
**Fix:** App password is wrong or expired. Generate new one.

### Error: "SMTPException: STARTTLS extension not supported"
**Fix:** Check EMAIL_USE_TLS = True and EMAIL_PORT = 587

### Error: "Connection refused"
**Fix:** Firewall blocking SMTP. Check antivirus/Windows Firewall.

### Error: "Username and Password not accepted"
**Fix:** 
- Enable 2-Factor Authentication on Gmail
- Use App Password (NOT your regular Gmail password)

---

## 🔍 Current Email Configuration

**File:** `cacaoguard/settings.py` (Line 205-211)

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'jardinesjohnlloyd@gmail.com'       
EMAIL_HOST_PASSWORD = 'mfmd cwuf znij zmmt'  # ⚠️ MAY BE EXPIRED
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

---

## 📨 What Emails Are Sent

### 1. Order Status Change (Automatic)
**Triggered:** When admin updates order status
**Recipients:** Customer who placed the order
**Templates:**
- ✅ Order Confirmed
- 📦 Order Processing  
- 🚚 Order Shipped
- ✨ Order Delivered
- ❌ Order Cancelled

**File:** `mainapp/views.py` → `send_status_change_email()` (Line 2323)

### 2. Welcome Email (Optional)
**Triggered:** Manual call to `/send-welcome-email/`
**Recipients:** New users

**File:** `mainapp/views.py` → `send_welcome_email()` (Line 597)

### 3. Password Reset (Firebase)
**Triggered:** User clicks "Forgot Password"
**Recipients:** User requesting reset
**Note:** Handled by Firebase Auth (separate from Django email)

**File:** `mainapp/views.py` (Line 541, 561)

---

## 🎯 Recommended Solution

**For Production:** Use **SendGrid** (Option 2)
- ✅ More reliable than Gmail
- ✅ Better deliverability
- ✅ Email analytics dashboard
- ✅ 100 free emails/day
- ✅ No 2FA hassles

**For Development:** Use **Console Backend** (Option 3)
- ✅ No setup needed
- ✅ See emails in terminal
- ✅ Fast testing

---

## 🚀 Quick Fix (5 minutes)

1. Visit: https://myaccount.google.com/apppasswords
2. Generate new app password
3. Edit `settings.py` line 210:
   ```python
   EMAIL_HOST_PASSWORD = 'new-password-here'  # No spaces!
   ```
4. Restart server:
   ```powershell
   python manage.py runserver
   ```
5. Test order status change in admin panel

---

## 📞 Support

If still not working after trying all options, check:
- Django logs for error messages
- Gmail account security settings
- Firewall/antivirus blocking port 587
- Internet connectivity

---

**Last Updated:** December 4, 2025  
**Status:** Awaiting email configuration fix
