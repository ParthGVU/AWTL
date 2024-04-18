import random
from flask import Flask, Response, request, render_template, redirect, url_for, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text  # Import text for SQL queries
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_data.db'
db = SQLAlchemy(app)


def generate_otp():
    return str(random.randint(10000, 99999))


# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)  # No hashing applied
    mobile = db.Column(db.String(15), nullable=False)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['username']
        password = request.form['password']

        if name == "admin" and password == "123":
            # Fetch all users from the database
            users = User.query.all()
            return render_template('admin.html', users=users)

        # Use SQLAlchemy session to execute SQL select statement
        # Explicitly declare the SQL query as text to resolve the error
        query = text(f"SELECT * FROM User WHERE name=:name AND password=:password")
        user = db.session.execute(query, {'name': name, 'password': password}).first()

        if user:
            send_otp_to_email(user.email)
            return render_template('otp1.html')
        else:
            return 'Login failed. Please check your username and password.'

    return render_template('login.html')


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


@app.route('/otp', methods=['GET', 'POST'])
def otp():
    if request.method == 'POST':
        user_otp = request.form['otp']

        if user_otp == g.otp:
            print("true")
            return render_template('welcome.html')
        else:
            print("false")

    return render_template('otp1.html')


def send_otp_to_email(receiver_email):
    # Sender's email and password
    sender_email = "mickeymouseparth@gmail.com"
    sender_password = "lizr yong lnpz gxzy"

    # Generate an OTP
    g.otp = generate_otp()  # Storing OTP in context

    # Create the message with the OTP
    message_body = f"Your OTP is: {g.otp}"
    subject = "OTP Verification"

    # Create an email message
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


@app.route('/insecure', methods=['GET', 'POST'])
def insecure_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Injected SQL query with correct syntax
        query = text(f"SELECT * FROM User WHERE name='{username}' AND (password='{password}')")
        user = db.session.execute(query).first()

        if user:
            g.otp = generate_otp()  # Store OTP in the context
            return redirect(url_for('otp'))
        else:
            return 'Login failed. Please check your username and password.'

    return render_template('insecure.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
