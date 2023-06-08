from flask import Flask, request, render_template, session, redirect, url_for, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import re
from bson.objectid import ObjectId
import os

app = Flask(__name__)
app.secret_key = 'your secret key'
app.config['UPLOAD_FOLDER'] = 'UPLOAD_FOLDER'

client = MongoClient('mongodb://localhost:27017/')
db = client['hosting-platform']

# Initialize the Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    u = db.users.find_one({"_id": ObjectId(user_id)})
    if not u:
        return None
    return User(str(u['_id']))

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('fname')
        last_name = request.form.get('lname')
        email = request.form.get('email')
        password = request.form.get('password')

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return 'Invalid email address'

        if db.users.find_one({'email': email}):
            return 'Email already registered'

        hashed_password = generate_password_hash(password)

        user = db.users.insert_one({
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': hashed_password,
        })

        user_obj = User(str(user.inserted_id))
        login_user(user_obj)

        return redirect(url_for('dashboard'))
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = db.users.find_one({'email': email})

        if user and check_password_hash(user['password'], password):
            user_obj = User(str(user['_id']))
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid email or password'
    else:
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'You have been logged out.'

@app.route('/dashboard')
@login_required
def dashboard():
    websites = db.websites.find({'user_id': current_user.id})
    return render_template('dashboard.html', websites=websites)
    
    # Get the user's websites from the database
    websites = db.websites.find({'user_id': session['user_id']})

    return render_template('dashboard.html', websites=websites)


@app.route('/create_website', methods=['POST'])
def create_website():
    # Check if a user is logged in
    if 'user_id' not in session:
        return 'You are not logged in.'

    # Get the data from the form
    name = request.form.get('name')

    # Check if a website with the same name already exists
    if db.websites.find_one({'name': name, 'user_id': session['user_id']}):
        return 'Website name already exists'

    # Insert the data into the 'websites' collection
    website = db.websites.insert_one({
        'name': name,
        'user_id': session['user_id'],
        'status': 'stopped',  # The website is initially stopped
    })

    # Create a folder for the website
    website_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(website.inserted_id))
    os.makedirs(website_folder)

    return redirect(url_for('dashboard'))


@app.route('/start_website/<website_id>')
def start_website(website_id):
    # Check if a user is logged in
    if 'user_id' not in session:
        return 'You are not logged in.'

    # Start the website
    db.websites.update_one({'_id': ObjectId(website_id)}, {'$set': {'status': 'running'}})

    return 'Website started!'


@app.route('/stop_website/<website_id>')
def stop_website(website_id):
    # Check if a user is logged in
    if 'user_id' not in session:
        return 'You are not logged in.'

    # Stop the website
    db.websites.update_one({'_id': ObjectId(website_id)}, {'$set': {'status': 'stopped'}})

    return 'Website stopped!'


@app.route('/delete_website/<website_id>')
def delete_website(website_id):
    # Check if a user is logged in
    if 'user_id' not in session:
        return 'You are not logged in.'

    # Delete the website
    db.websites.delete_one({'_id': ObjectId(website_id), 'user_id': session['user_id']})

    return redirect(url_for('dashboard'))



@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if a user is logged in
        if 'user_id' not in session:
            return 'You are not logged in.'

        # Get the uploaded file
        file = request.files['file']

        # Check if the file is valid
        if file and allowed_file(file.filename):
            # Save the file to the upload folder
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Do any further processing as needed

            return 'File uploaded successfully'

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

ALLOWED_EXTENSIONS = {'html', 'css', 'js', 'png', 'jpg', 'jpeg', 'gif'}
            
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_website/<website_id>', methods=['POST'])
def upload_website_file(website_id):
    # Check if a user is logged in
    if 'user_id' not in session:
        return 'You are not logged in.'

    # Check if the website belongs to the user
    website = db.websites.find_one({'_id': ObjectId(website_id), 'user_id': session['user_id']})
    if not website:
        return 'Website not found'

    # Get the uploaded file
    file = request.files['file']
    if not file:
        return 'No file selected'

    # Save the file to the website folder
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], str(website_id), filename))

    # Perform any further processing as needed

    return 'File uploaded successfully'

@app.route('/sites/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/websites/<website_id>')
def render_website(website_id):
    # Check if a user is logged in
    if 'user_id' not in session:
        return 'You are not logged in.'

    # Get the website details from the database
    website = db.websites.find_one({'_id': ObjectId(website_id), 'user_id': session['user_id']})

    if not website:
        return 'Website not found'

    # Serve the index.html file
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], str(website_id)), 'index.html')


if __name__ == '__main__':
    app.run(debug=True)
