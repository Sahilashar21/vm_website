# Firebase Authentication Setup Guide

This guide will help you set up Firebase authentication with Google and Gmail login for your Vidyarthi Mitra website.

## Prerequisites
- A Google account
- Firebase project (free tier available)
- Python 3.7+
- Flask application running

## Step 1: Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a new project"
3. Enter your project name: `vidyarthi-mitra` (or any name)
4. Uncheck "Enable Google Analytics" (optional for testing)
5. Click "Create project"
6. Wait for the project to be created, then click "Continue"

## Step 2: Enable Authentication Methods

### Set up Email/Password Authentication:
1. In Firebase Console, go to **Authentication** (left sidebar → Build → Authentication)
2. Click on the **Sign-in method** tab
3. Click **Email/Password**
4. Enable both "Email/Password" and "Email link (passwordless sign-in)" (optional)
5. Click Save

### Set up Google OAuth:
1. In the **Sign-in method** tab, click **Google**
2. Toggle the Enable switch to ON
3. Enter your project name as the "Project support email"
4. Click Save

## Step 3: Get Your Firebase Configuration

1. In Firebase Console, click the ⚙️ (Settings) icon → **Project Settings**
2. Scroll down to find "Your apps"
3. Click on **Web** icon (</> symbol) to create a new web app
4. Enter app nickname: `vidyarthi-mitra`
5. Click "Register app"
6. You'll see your Firebase config - **COPY THIS**

Your config will look like:
```javascript
{
  apiKey: "AIzaSyB...",
  authDomain: "vidyarthi-mitra.firebaseapp.com",
  projectId: "vidyarthi-mitra",
  storageBucket: "vidyarthi-mitra.appspot.com",
  messagingSenderId: "...",
  appId: "..."
}
```

## Step 4: Configure Your Application

### 1. Create/Update `.env` file in your project root:

```bash
# Copy the example file
cp .env.example .env
```

### 2. Edit `.env` with your Firebase credentials:

```
FIREBASE_API_KEY=AIzaSyB...
FIREBASE_AUTH_DOMAIN=vidyarthi-mitra.firebaseapp.com
FIREBASE_PROJECT_ID=vidyarthi-mitra
FIREBASE_STORAGE_BUCKET=vidyarthi-mitra.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123456789
FIREBASE_APP_ID=1:123456789:web:abc123def456

FLASK_ENV=development
SECRET_KEY=your_super_secret_key_here_change_in_production
```

## Step 5: Set Up Google OAuth Consent Screen (for Google Sign-In)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your Firebase project
3. Go to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **OAuth 2.0 Client ID**
5. Choose **Web application**
6. Add Authorized redirect URIs:
   - `http://localhost:5000`
   - `http://localhost:5000/login`
   - Your production domain (when deployed)
7. Click Create
8. Note your **Client ID** and **Client Secret**

## Step 6: Test Your Setup

1. **Start your Flask app:**
```bash
python app.py
```

2. **Visit the authentication pages:**
   - Login: http://localhost:5000/login
   - Sign Up: http://localhost:5000/signup

3. **Test different authentication methods:**
   - Email/Password signup
   - Google sign-in
   - Gmail sign-in (same as Google OAuth)

## Features Implemented

✅ **Email/Password Authentication**
- Sign up with email and password
- Password strength indicator
- Password confirmation validation

✅ **Google OAuth Authentication**
- One-click Google sign-in
- Automatic profile population

✅ **Gmail Authentication**
- Uses Google OAuth (Gmail is Google's email service)
- Seamless Gmail account login

✅ **User Session Management**
- Session storage in Flask
- User profile information saved
- Logout functionality

✅ **Security Features**
- HTTPS recommended for production
- CSRF protection ready
- Secure session storage
- Password strength validation

## Authentication Routes

### Public Routes
- `GET /login` - Login page
- `GET /signup` - Sign up page
- `GET /logout` - Logout and clear session

### API Routes (for JavaScript)
- `POST /auth/set-user` - Save user to session after Firebase auth
- `GET /auth/get-user` - Get current user from session
- `GET /auth/check-auth` - Check if user is authenticated

## How to Use the `@login_required` Decorator

To protect routes that require authentication, use the decorator:

```python
@app.route("/profile")
@login_required
def profile():
    user = session.get('user')
    return render_template('profile.html', user=user)
```

## Production Checklist

- [ ] Update `SECRET_KEY` in `.env` to a strong value
- [ ] Enable HTTPS/SSL
- [ ] Update Firebase authorized redirect URIs to production domain
- [ ] Set `FLASK_ENV=production`
- [ ] Remove `.env` from version control (add to `.gitignore`)
- [ ] Store `.env` safely on production server
- [ ] Enable Firebase security rules
- [ ] Set up custom domain for error handling
- [ ] Review Firebase Authentication limits and quotas

## Troubleshooting

### "Firebase is not defined"
- Make sure Firebase SDK is loaded in your template
- Check browser console for script loading errors

### "Popup closed by user"
- User clicked cancel or closed the popup
- This is handled gracefully in the code

### "Invalid API key"
- Check your Firebase config in login.html and signup.html
- Verify API Key in Firebase Console → Settings

### Users not being saved to session
- Check Flask secret key is set
- Verify `/auth/set-user` endpoint is working
- Check browser console for errors

### CORS errors
- Make sure your domain is listed in Firebase authorized domains
- Check Firebase security settings

## Additional Resources

- [Firebase Authentication Docs](https://firebase.google.com/docs/auth)
- [Firebase Python Admin SDK](https://firebase.google.com/docs/database/admin/start)
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
- [Flask Session Management](https://flask.palletsprojects.com/en/2.3.x/api/#sessions)

## Next Steps

1. Add user profile page
2. Add password reset functionality
3. Add email verification
4. Add two-factor authentication (2FA)
5. Store user profile data in database
6. Add role-based access control (RBAC)

## Support

For Firebase issues, visit: https://firebase.google.com/support
For Python/Flask issues, visit: https://stackoverflow.com/questions/tagged/flask
