from flask import Flask, render_template,request,redirect,url_for,jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin,login_user ,current_user, login_required
from flask import session
from flask_session import Session
from sqlalchemy import Float
from flask_migrate import Migrate
from models import db
from flask_mail import Mail,Message

import os
import json
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = f"sqlite:///{os.path.join(project_dir, 'mydatabase.db')}"
app = Flask(__name__)
migrate = Migrate(app, db)  # 'db' is your SQLAlchemy database instance
app.config["SQLALCHEMY_DATABASE_URI"]= database_file
app.config['SECRET_KEY'] = os.urandom(24).hex()  # Set a random secret key
app.config["SESSION_TYPE"] = "filesystem"  # You can change this to other session types as needed
app.config["SESSION_PERMANENT"] = False
# email config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'rajesh.khanvilkar@gmail.com'  # Your Gmail email address
app.config['MAIL_PASSWORD'] = 'mrjl cejo bpbo hgay'  # Your Gmail password
app.config['MAIL_DEFAULT_SENDER'] = 'rajesh.khanvilkar@gmail.com'  # Your Gmail email address

mail = Mail(app)

Session(app)

db = SQLAlchemy(app)

migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # This function is required by Flask-Login. It loads a user given the user ID.
    return User.query.get(int(user_id))

class Book(db.Model):
    name = db.Column(db.String(100),unique=True,nullable = False,primary_key=True)
    author = db.Column(db.String(100),nullable = False)
    image_link = db.Column(db.String(255))
    price = db.Column(Float,nullable=False) 

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='user')  # 'user' or 'admin'

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500))
    rating = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_name = db.Column(db.String(100), db.ForeignKey('book.name'), nullable=False)
    user = db.relationship('User', backref=db.backref('reviews', lazy=True))
    book = db.relationship('Book', backref=db.backref('reviews', lazy=True))

#from models import User, Admin  # Import User and Admin directly
with app.app_context():
    #db.drop_all()
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
       username = request.form['username']
       password = request.form['password']
       
        # Check if the username and password match any user in the database
       user = User.query.filter_by(username=username).first()
       
       if user and check_password_hash(user.password, password) and user.role=='user':
            # If it's an admin user, log in and redirect to the admin dashboard
            login_user(user)
            return redirect(url_for('books'))
    
       else:
            # If login fails, render the login form with an error message
            return render_template('login.html', error='Invalid username or password')
      
    else:
        # If it's a GET request, just render the login form
        return render_template('login.html')
    
# Function to send welcome email
def send_welcome_email(user_email):
    subject = 'Welcome to Our Online Book Store'
    body = f'Thank you for registering with our online book store. We hope you enjoy your experience!'

    message = Message(subject=subject, recipients=[user_email], body=body)
    mail.send(message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Add your registration logic here
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Add your validation and registration logic (check if username already exists, password matching, etc.)

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
         # Assuming you save the user in a database, you can get their email
        user_email = "bhoomilandge@gmail.com"  # Replace with the actual email

        # Call the function to send a welcome email
        send_welcome_email(user_email)
        new_user = User(username=username, password=hashed_password, role='user')
        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')  # Redirect to login page after successful registration

    # GET request for displaying the registration form
    return render_template('register.html')

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    # Ensure the user is an admin before allowing access to the admin dashboard
    if current_user.is_authenticated and current_user.role == 'admin':
        return render_template('admin_dashboard.html')
    else:
        # Redirect to a non-admin page or show an error message
        return redirect(url_for('home'))
    
@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validate the form data (e.g., check if passwords match)

        # Create a new admin user and add it to the database
        if password == confirm_password:
            hashed_password = generate_password_hash(password)
            new_admin = User(username=username, password=hashed_password, role='admin')
            db.session.add(new_admin)
            db.session.commit()

            # Redirect to the admin login page after successful registration
            return redirect(url_for('admin_register'))
        else:
            # Handle the case where passwords don't match
            return render_template('admin_register.html', message="Passwords do not match.")

    # If it's a GET request, render the admin registration form
    return render_template('admin/admin_register.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username and password match any admin user in the database
        admin = User.query.filter_by(username=username, role='admin').first()

        if admin and check_password_hash(admin.password, password):
            login_user(admin) 
            return redirect(url_for('admin_dashboard'))

        else:
            # If login fails, render the admin login form with an error message
            return render_template('admin/admin_login.html', error='Invalid username or password')

    # If it's a GET request, just render the admin login form
    return render_template('admin/admin_login.html')


@app.route('/addbook')
def addbook():
    return render_template('addbook.html')

@app.route('/submitbook',methods=['POST'])
def submitbook():
    name = request.form['name']
    author = request.form['author']
    image_link = request.form['image_link']
    price = request.form['price']
    book = Book(name=name,author=author,image_link=image_link,price=price)
    print("Form Data:", request.form)
    db.session.add(book)
    db.session.commit()
    # Inside the submitbook route


    return redirect('/books')

@app.route('/update_session', methods=['POST'])
def update_session():
    cart_data = request.get_json().get('cart', {})
    
    # Update the session with the received cart data
    session['cart'] = cart_data
    session.modified = True
    
    return jsonify({'message': 'Session updated successfully'})
   
@app.route('/updatebooks')
def updatebooks():
    books = Book.query.all()
    return render_template('updatebooks.html',books=books)

@app.route('/update',methods=['POST'])
def update():
    newname = request.form['newname']
    oldname = request.form['oldname']
    newauthor = request.form['newauthor']

    book = Book.query.filter_by(name=oldname).first()
    
    book.name = newname
    book.author = newauthor
    db.session.commit()

    return redirect('/books')

@app.route('/delete', methods=['POST'])
def delete():
    name = request.form['name']
    book = Book.query.filter_by(name=name).first()
    db.session.delete(book)
    db.session.commit()

    return redirect('/books')


@app.route('/books',methods=['GET', 'POST'])
def books():
    if request.method == 'POST':
        search_query = request.form['search_query']
        if search_query:
            books = Book.query.filter(
                (Book.name.ilike(f"%{search_query}%")) | (Book.author.ilike(f"%{search_query}%"))
                ).all()
        else:
            books = Book.query.all()
    else:
        books = Book.query.all()
    return render_template('books.html',books=books)

@app.route('/order')
def order():
     # Retrieve cart data from the query parameter
    cart_data_json = request.args.get('cart')

    # Parse the JSON data
    cart_data = json.loads(cart_data_json) if cart_data_json else {}
    print(cart_data)
    return render_template('order_details.html', cart_data=cart_data)

if __name__ == "__main__":
    app.run(debug=True)
