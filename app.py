from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from werkzeug.utils import secure_filename
# import time
# filename = str(int(time.time())) + "_" + secure_filename(file.filename)
from datetime import datetime
import pytz
import requests
import random
import smtplib
from email.mime.text import MIMEText
EMAIL_ADDRESS = "himanshi.kumawat.1202@gmail.com"
EMAIL_PASSWORD = "flnjxfgarlqlmnmh"
def send_otp_email(to_email, otp):
    subject = "StayConnect OTP Verification"
    body = f"Your OTP is {otp}"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully")
    except Exception as e:
        print("Email Error:", e)
# from twilio.rest import Client

# account_sid = "AC014b73f47c5b61500a44f1de741c6b57"
# auth_token = "f0866e60628edb11381b3eccb007c2a6"
# twilio_number = "+12602547973"   # Twilio number

# client = Client(account_sid, auth_token)
IST = pytz.timezone('Asia/Kolkata')

def ist_now():
    return datetime.now(IST)



app = Flask(__name__)
app.secret_key = "stayconnect_secret"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ================= DATABASE MODELS =================
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg','gif', 'pdf', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

RESOURCE_FOLDER = 'static/resources'
app.config['RESOURCE_FOLDER'] = RESOURCE_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(20))
    phone = db.Column(db.String(15))

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student = db.Column(db.String(100))
    category = db.Column(db.String(50))
    description = db.Column(db.String(300))
    image = db.Column(db.String(200))   # 👈 NEW
    status = db.Column(db.String(20), default="Pending")
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    attachment = db.Column(db.String(200))  # ✅ ADD THIS


class Emergency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    contact = db.Column(db.String(20))

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    filename = db.Column(db.String(200))
    uploaded_by = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Rule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500))
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    roll_no = db.Column(db.String(50), unique=True)
    branch = db.Column(db.String(50))
    year = db.Column(db.String(10))
    hostel = db.Column(db.String(50))
    room = db.Column(db.String(20))
    phone = db.Column(db.String(15))

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=ist_now)


class EntryExit(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))  # 🔥 LINK

    type = db.Column(db.String(10), nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, default=ist_now)

    student = db.relationship('Student')  # 🔥 RELATION

# ================= AUTH =================
@app.route('/announcements')
def announcements():
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template(
        'announcements.html',
        announcements=announcements,
        role=session.get('role')   # ✅ PASS ROLE
    )

@app.route('/add_announcement', methods=['POST'])
def add_announcement():
    if session.get('role') != "Admin":
        return redirect('/dashboard')

    ann = Announcement(
        title=request.form['title'],
        message=request.form['message']
    )
    db.session.add(ann)
    db.session.commit()

    return redirect('/announcements')

@app.route('/edit_announcement/<int:id>', methods=['GET', 'POST'])
def edit_announcement(id):
    if session.get('role') != 'Admin':
        return redirect(url_for('announcements'))

    announcement = Announcement.query.get_or_404(id)

    if request.method == 'POST':
        announcement.title = request.form['title']
        announcement.message = request.form['message']
        db.session.commit()
        return redirect(url_for('announcements'))

    return render_template('edit_announcement.html', announcement=announcement)
    return render_template('edit_announcement.html', announcement=announcement)

@app.route('/students')
def students_page():
    role = session.get('role')
    name = session.get('name')   # SAFE access

    if role == "Student" and name:
        student = Student.query.filter_by(name=name).first()
        return render_template(
            "students.html",
            students=[student] if student else [],
            role=role
        )

    return render_template(
        "students.html",
        students=Student.query.all(),
        role=role
    )

@app.route('/add_student', methods=['POST'])
def add_student():
    if session.get('role') != "Admin":
        return redirect('/students')

    s = Student(
        name=request.form['name'],
        roll_no=request.form['roll_no'],
        branch=request.form['branch'],
        year=request.form['year'],
        hostel=request.form['hostel'],
        room=request.form['room'],
        phone=request.form['phone']
    )
    db.session.add(s)
    db.session.commit()
    return redirect('/students')
@app.route('/delete_student/<int:id>')
def delete_student(id):
    if session.get('role') != "Admin":
        return redirect('/students')

    s = Student.query.get(id)
    if s:
        db.session.delete(s)
        db.session.commit()
    return redirect('/students')

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/register")
def register_page():
    return render_template("register.html")
@app.route('/resources')
def resources_page():
    return render_template(
        "resources.html",
        resources=Resource.query.all(),
        role=session.get('role'),
        user=session.get('name')
    )

@app.route('/upload_resource', methods=['POST'])
def upload_resource():
    if session.get('role') != "Student":
        return redirect('/resources')

    file = request.files['file']
    if file and file.filename != "":
        filename = secure_filename(file.filename)

        # 🔥 ENSURE FOLDER EXISTS
        os.makedirs(app.config['RESOURCE_FOLDER'], exist_ok=True)

        path = os.path.join(app.config['RESOURCE_FOLDER'], filename)
        file.save(path)

        res = Resource(
            title=request.form['title'],
            filename=filename,
            uploaded_by=session.get('name')
        )
        db.session.add(res)
        db.session.commit()

    return redirect('/resources')

@app.route('/rules')
def rules_page():
    return render_template(
        "rules.html",
        rules=Rule.query.all(),
        role=session.get('role')
    )
@app.route('/add_rule', methods=['POST'])
def add_rule():
    if session.get('role') == "Admin":
        rule = Rule(content=request.form['content'])
        db.session.add(rule)
        db.session.commit()
    return redirect('/rules')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']

    # Check if username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return "Username already exists. Please choose a different username."

    user = User(
        name=request.form['name'],
        username=username,
        phone=request.form['phone'],
        role=request.form['role'],
        password=generate_password_hash(request.form['password'])
    )

    db.session.add(user)
    db.session.commit()
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(username=request.form['username']).first()

    if user and check_password_hash(user.password, request.form['password']):
        session.clear()  # 👈 IMPORTANT
        session['username'] = user.username
        session['name'] = user.name
        session['role'] = user.role
        return redirect('/dashboard')

    flash('Invalid login. Please check your username and password.', 'error')
    return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ================= DASHBOARD =================

@app.route('/dashboard')
def dashboard():
    if not session.get('role'):
        return redirect('/')

    return render_template(
        "dashboard.html",
        user=session.get('name', 'User'),
        role=session.get('role'),
        complaints=Complaint.query.all(),
        notices=Notice.query.all()
    )

# ================= COMPLAINTS =================

@app.route('/complaints')
def complaints_page():
    return render_template(
        "complaints.html",
        complaints=Complaint.query.order_by(Complaint.id.desc()).all(),
        role=session.get('role')
    )

@app.route('/add_complaint', methods=['POST'])
def add_complaint():
    if session.get('role') != "Student":
        return redirect('/complaints')

    image_filename = None

    # 🔥 FILE HANDLING
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != "":
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filename = secure_filename(file.filename)
            image_filename = filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    complaint = Complaint(
        student=session.get('name'),
        category=request.form['category'],
        description=request.form['description'],
        image=image_filename
    )

    db.session.add(complaint)
    db.session.commit()

    return redirect('/complaints')

# ================= NOTICES =================
@app.route('/update_status/<int:complaint_id>', methods=['POST'])
def update_status(complaint_id):
    # Only admin can change status
    if session.get('role') != "Admin":
        return redirect('/complaints')

    complaint = Complaint.query.get(complaint_id)
    if complaint:
        complaint.status = request.form['status']
        db.session.commit()

    return redirect('/complaints')

@app.route('/notices')
def notices_page():
    return render_template(
        "notices.html",
        notices=Notice.query.order_by(Notice.id.desc()).all(),
        role=session['role']
    )

@app.route('/add_notice', methods=['POST'])
def add_notice():
    if session.get('role') != 'Admin':
        return redirect('/notices')

    title = request.form['title']
    description = request.form['description']

    file = request.files.get('attachment')
    filename = None

    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    notice = Notice(
        title=title,
        description=description,
        attachment=filename
    )

    db.session.add(notice)
    db.session.commit()

    return redirect('/notices')


@app.route('/entry')
def entry_page():
    if session.get('role') != "Admin":
        return redirect('/dashboard')   # 🔒 BLOCK

    students = Student.query.all()
    logs = EntryExit.query.filter_by(type="Entry").all()

    return render_template(
        "entry.html",
        students=students,
        logs=logs,
        role=session.get('role')
    )
@app.route('/exit')
def exit_page():
    if session.get('role') != "Admin":
        return redirect('/dashboard')   # 🔒 BLOCK

    students = Student.query.all()
    logs = EntryExit.query.filter_by(type="Exit").all()

    return render_template(
        "exit.html",
        students=students,
        logs=logs,
        role=session.get('role')
    )
# ================= ENTRY / EXIT =================
@app.route('/entry_exit')
def entry_exit():
    role = session.get('role')

    students = Student.query.all()   # 🔥 ADD THIS

    if role == "Admin":
        logs = EntryExit.query.all()
    elif role == "Student":
        student = Student.query.filter_by(name=session.get('name')).first()
        logs = EntryExit.query.filter_by(student_id=student.id).all()
    else:
        logs = EntryExit.query.all()

    return render_template(
        "entry_exit.html",
        role=role,
        logs=logs,
        students=students   # 🔥 PASS
    )

@app.route('/admin_add_entry_exit', methods=['POST'])
def admin_add_entry_exit():
    if session.get('role') != "Admin":
        return redirect('/dashboard')   # 🔒 protect

    student_id = request.form['student_id']
    type = request.form['type']
    reason = request.form['reason']

    log = EntryExit(
        student_id=student_id,
        type=type,
        reason=reason
    )

    db.session.add(log)
    db.session.commit()

    if type == "Entry":
        return redirect(url_for('entry_page'))
    else:
        return redirect(url_for('exit_page'))
@app.route('/update_entry_exit/<int:id>', methods=['POST'])
def update_entry_exit(id):
    if session.get('role') != "Admin":
        return redirect('/dashboard')   # 🔒 BLOCK

    log = EntryExit.query.get(id)

    if log:
        log.type = request.form['type']
        db.session.commit()

    if log.type == "Entry":
        return redirect('/entry')
    else:
        return redirect('/exit')
# ================= EMERGENCY =================

@app.route('/emergency')
def emergency_page():
    return render_template(
        "emergency.html",
        contacts=Emergency.query.all()
    )

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        user = User.query.filter_by(username=username).first()

        if user:
            otp = str(random.randint(100000, 999999))

            session['otp'] = otp
            session['reset_user'] = user.id

            send_otp_email(email, otp)

            return redirect('/verify_otp')

        else:
            return "Invalid details ❌"

    return render_template("forgot_password.html")

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        new_password = request.form['new_password']

        if entered_otp == session.get('otp'):
            user = User.query.get(session.get('reset_user'))

            from werkzeug.security import generate_password_hash
            user.password = generate_password_hash(new_password)

            db.session.commit()

            session.pop('otp', None)
            session.pop('reset_user', None)

            return "Password reset successful ✅ <a href='/login'>Login</a>"
        else:
            return "Invalid OTP ❌"

    return render_template("verify_otp.html")

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect('/')

    return render_template(
        'profile.html',
        user=session['user'],
        role=session['role']
    )

@app.route("/delete_complaint/<int:id>", methods=["POST"])
def delete_complaint(id):
    complaint = Complaint.query.get(id)
    if complaint:
        if complaint.image:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], complaint.image)
            if os.path.exists(image_path):
                os.remove(image_path)

        db.session.delete(complaint)
        db.session.commit()

    return redirect("/complaints")


# Ensure database tables exist whenever the app starts
with app.app_context():
    db.create_all()


# ================= RUN =================
if __name__ == "__main__":
    with app.app_context():

        db.create_all()

        from werkzeug.security import generate_password_hash

        existing_admin = User.query.filter_by(username="admin").first()

        if not existing_admin:
            admin = User(
                name="Admin",
                username="admin",
                phone="9999999999",
                role="Admin",
                password=generate_password_hash("admin123")
            )

            db.session.add(admin)
            db.session.commit()
            print("Admin created successfully ✅")

        else:
            print("Admin already exists 👍")

    app.run(debug=True, use_reloader=False)