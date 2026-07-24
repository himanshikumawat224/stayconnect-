# StayConnect

A Flask-based student and hostel management portal with support for announcements, complaints, resources, emergency contacts, attendance entry/exit logging, notices, rules, and OTP-based password reset.

## Features

- User registration and login
- Role-based access for `Admin` and `Student`
- Admin dashboard with complaint and notice management
- Student complaint submission with optional image upload
- Upload and view shared resources
- Manage and display campus rules
- View emergency contact list
- Entry/exit logging for students
- Forgot password flow with OTP email verification

## Project Structure

- `app.py` - Flask application and route definitions
- `requirements.txt` - Python dependencies
- `templates/` - HTML templates for the user interface
- `static/` - CSS, JavaScript, uploads, and other static assets

## Requirements

- Python 3.10+ (or compatible Python 3 version)
- `virtualenv` or built-in `venv` recommended

## Setup

1. Create and activate a virtual environment:

```powershell
python -m venv venv
& .\venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the app:

```powershell
python app.py
```

4. Open your browser at:

```text
http://127.0.0.1:5000
```

## Default Admin Account

The app automatically creates a default admin user if one does not already exist.

- Username: `admin`
- Password: `admin123`

## Notes

- The app uses SQLite for the database: `database.db`
- File uploads are stored in `static/uploads`
- Resource uploads are stored in `static/resources`
- OTP emails are sent via Gmail SMTP using the credentials configured in `app.py`

> Important: For production use, do not store email credentials directly in source code. Use environment variables or a secure configuration mechanism.

