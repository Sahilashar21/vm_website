# Vidyarthi Mitra - Educational Guidance Platform

A comprehensive web platform for discovering and comparing universities, colleges, and courses in India.

## 🚀 Features

### Core Features
- **University Directory** - Browse and filter top universities by state and criteria
- **College Directory** - Search and compare colleges across India
- **Course Finder** - Discover courses and streams
- **University Details** - Comprehensive information about each university
- **Exams Guide** - Information about entrance exams
- **Mock Tests** - Practice tests and mock exams
- **Admissions Support** - Admissions guidance and procedures
- **Expert Counselling** - Access to education counselors
- **Scholarship Finder** - Available scholarships and aid
- **DTE Counseling** - Direct Admissions Through Entrance exam

### Authentication & Users
- **Email/Password Registration** - Create account with email
- **Google Sign-In** - One-click authentication with Google
- **Gmail Sign-In** - Gmail account support
- **User Sessions** - Persistent login sessions
- **Secure Logout** - Clear sessions and cookies

## 📋 Project Structure

```
VM_website/
├── app.py                      # Flask application and routes
├── static/                     # Static files (CSS, JS, images)
├── templates/                  # HTML templates
│   ├── index.html             # Home page
│   ├── login.html             # Login page with Firebase auth
│   ├── signup.html            # Registration page
│   ├── universities.html      # Universities directory
│   ├── colleges.html          # Colleges directory
│   ├── courses.html           # Courses directory
│   ├── university_detail.html # Individual university profile
│   ├── inner_page.html        # Generic content page template
│   └── not_found.html         # 404 error page
├── .env.example               # Environment variables template
├── requirements.txt           # Python dependencies
├── FIREBASE_SETUP.md          # Firebase authentication setup guide
└── README.md                  # This file
```

## 🛠️ Technology Stack

### Backend
- **Python 3.13.5** - Programming language
- **Flask** - Web framework
- **Jinja2** - Template engine
- **python-dotenv** - Environment variable management
- **firebase-admin** - Firebase Admin SDK

### Frontend
- **Bootstrap 5.3.2** - CSS framework
- **JavaScript** - Client-side logic
- **jQuery** - DOM manipulation
- **Font Awesome 6.5.2** - Icons
- **Google Fonts** - Poppins, Inter typefaces

### Authentication
- **Firebase** - Authentication service
- **Google OAuth 2.0** - Social sign-in

## ⚙️ Installation & Setup

### 1. Clone/Download the Project
```bash
cd VM_website
```

### 2. Create Python Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Set Up Firebase (Important!)
- Follow the detailed guide in [FIREBASE_SETUP.md](FIREBASE_SETUP.md)
- Create `.env` file with your Firebase credentials
- **Do not share your `.env` file publicly**

### 6. Run the Application
```bash
python app.py
```

The application will be available at: **http://localhost:5000**

## 📦 Dependencies

```
Flask==2.3.x
firebase-admin==6.x
python-dotenv==1.0.x
```

## 🔐 Authentication Setup

### Quick Start
1. Get Firebase credentials from [FIREBASE_SETUP.md](FIREBASE_SETUP.md)
2. Create `.env` file:
   ```bash
   cp .env.example .env
   ```
3. Fill in your Firebase API keys
4. Restart Flask server
5. Test at http://localhost:5000/login

### Login Methods
- **Email/Password** - Register and login with email
- **Google** - One-click login with Google account
- **Gmail** - Login using Gmail (part of Google OAuth)

## 📄 Routes & Pages

### Public Routes
| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Home page with hero section and features |
| `/login` | GET | Login page |
| `/signup` | GET | Registration page |
| `/logout` | GET | Logout and clear session |
| `/universities` | GET | Browse universities |
| `/university/<name>` | GET | University detail page |
| `/colleges` | GET | Browse colleges |
| `/courses` | GET | Browse courses |
| `/exams` | GET | Exams information |
| `/mock-exams` | GET | Mock tests page |
| `/admissions` | GET | Admissions guide |
| `/counselling` | GET | Counselling services |
| `/scholarship` | GET | Scholarship finder |
| `/dte` | GET | DTE counseling |

### Authentication API Routes
| Route | Method | Purpose |
|-------|--------|---------|
| `/auth/set-user` | POST | Save user to session (from Firebase) |
| `/auth/get-user` | GET | Get current user from session |
| `/auth/check-auth` | GET | Check if user is authenticated |

## 🔒 Protecting Routes

To add authentication to a route:

```python
from functools import wraps
from flask import session, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/profile')
@login_required
def profile():
    user = session.get('user')
    return render_template('profile.html', user=user)
```

## 🎨 Customization

### Change Colors
Edit `templates/index.html`:
```css
:root {
  --primary: #ff6b35;      /* Main brand color */
  --secondary: #1e3a8a;    /* Secondary color */
  --text-dark: #1e293b;    /* Text color */
}
```

### Add New Pages
1. Create HTML template in `templates/`
2. Add route in `app.py`
3. Add navigation link in navbar

### Add New Sections
1. Create HTML file in `templates/`
2. Add route using `render_section()` function:
```python
@app.route('/new-section')
def new_section():
    return render_section('new_section.html', 'New Section Title')
```

## 📊 Data Management

The application includes live data parsing from HTML content:
- Universities extracted from MARKUP
- Colleges data with filtering
- Courses organized by stream
- Caching system for performance

## 🚀 Deployment

### Before Deploying to Production
1. Change `FLASK_ENV` to `production` in `.env`
2. Generate strong `SECRET_KEY`
3. Set up HTTPS/SSL certificate
4. Update Firebase authorized domains
5. Configure error handling
6. Set up logging
7. Test all authentication flows

### Deployment Platforms
- **Heroku** - Easy deployment, free tier available
- **PythonAnywhere** - Python hosting
- **AWS** - EC2, Elastic Beanstalk
- **Google Cloud** - App Engine, Cloud Run
- **Azure** - App Service

## 🐛 Troubleshooting

### Flask not starting?
```bash
python -m flask run --debug
```

### Firebase authentication not working?
- Check `.env` file has correct API keys
- Verify Firebase project is created
- Check browser console for errors
- Review FIREBASE_SETUP.md

### Issues with virtual environment?
```bash
# Delete and recreate
rmdir venv /s  # Windows
rm -rf venv    # macOS/Linux

python -m venv venv
# Then activate and install dependencies
```

### Port 5000 already in use?
```bash
# Run on different port
python -c "from app import app; app.run(port=5001)"
```

## 📚 Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Firebase Docs](https://firebase.google.com/docs)
- [Bootstrap Docs](https://getbootstrap.com/docs)
- [Google OAuth Guide](https://developers.google.com/identity)

## 🤝 Contributing

1. Create a new branch: `git checkout -b feature/new-feature`
2. Make your changes
3. Test thoroughly
4. Commit changes: `git commit -am 'Add new feature'`
5. Push to branch: `git push origin feature/new-feature`
6. Submit pull request

## 📝 License

This project is open source and available under the MIT License.

## 📧 Support & Contact

For issues, questions, or suggestions:
- Check [FIREBASE_SETUP.md](FIREBASE_SETUP.md) for authentication help
- Review error messages in browser console
- Check Flask terminal output for server errors

## 🎯 Future Enhancements

- [ ] User profile page
- [ ] Save favorite universities/colleges
- [ ] Comparison tool
- [ ] User reviews and ratings
- [ ] Notifications for new content
- [ ] Mobile app
- [ ] Advanced search filters
- [ ] Chatbot for counseling
- [ ] Payment integration for premium features
- [ ] Analytics dashboard

## Version History

**v1.0.0** - Initial release
- Core university/college/course directory
- Firebase authentication system
- Email, Google, and Gmail sign-in
- Responsive design

---

**Last Updated:** 2024  
**Status:** Active Development
