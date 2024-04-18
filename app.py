import random
from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_data.db'
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)  # No hashing applied
    mobile = db.Column(db.String(15), nullable=False)

# Route for login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['username']
        password = request.form['password']

        if name == "admin" and password == "123":
            # Fetch all users from the database
            users = User.query.all()
            return render_template('admin.html', users=users)

        # Query the User table to find the user
        user = User.query.filter_by(name=name, password=password).first()

        if user:
            send_otp_to_email(user.email)
            return render_template('otp1.html')
        else:
            return 'Login failed. Please check your username and password.'

    return render_template('login.html')

# Route for user signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        email = request.form['email']
        password = request.form['password']
        mobile = request.form['mobile']

        # Create a new user object
        new_user = User(name=name, dob=dob, email=email, password=password, mobile=mobile)
        # Add the new user to the database session
        db.session.add(new_user)
        # Commit changes to the database
        db.session.commit()

        return render_template('login.html')

    return render_template('signup.html')

# Route for OTP verification
@app.route('/otp', methods=['GET', 'POST'])
def otp():
    if request.method == 'POST':
        user_otp = request.form['otp']

        # Validate OTP
        if user_otp == session.get('otp'):
            return render_template('welcome.html')
        else:
            return 'Invalid OTP. Please try again.'

    return render_template('otp1.html')

# Function to send OTP to the user's email
def send_otp_to_email(receiver_email):
    # Sender's email and password (you may need to use app-specific passwords for Gmail)
    sender_email = "mickeymouseparth@gmail.com"
    sender_password = "your_sender_password"

    # Generate OTP
    otp = generate_otp()
    session['otp'] = otp  # Store OTP in session for verification

    # Create email message
    message_body = f"Your OTP is: {otp}"
    subject = "OTP Verification"
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(message_body, "plain"))

    # Set up the SMTP server and send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print(f"OTP sent to {receiver_email}")
    except Exception as e:
        print(f"Failed to send OTP: {e}")

if __name__ == '__main__':
    app.secret_key = 'your_secret_key'  # Set a secret key for session management
    with app.app_context():
        db.create_all()
    app.run(debug=True)
