from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from wtforms import Form, StringField, PasswordField, validators
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from wtforms.fields import EmailField

# Create a Flask application
app = Flask(__name__, static_folder='static', static_url_path='')

# Set the secret key, which is needed for session to work
app.secret_key = 'your-secret-key'

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Initialize the limiter
limiter = Limiter(
    # app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Create a connection to MongoDB
client = MongoClient('mongodb://localhost:27017/')

# Connect to your database
db = client['myhosting']

# Connect to your collections
users = db['users']
tasks = db['tasks']


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = EmailField('Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [validators.Length(min=8, max=80),
                                          validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password')


@app.route('/', methods=['GET'])
def home_page():
    return app.send_static_file('index.html')


@app.route('/register', methods=['GET'])
def register_page():
    return app.send_static_file('register.html')


@app.route('/api/register', methods=['POST'])
@limiter.limit("10 per day")
def register():
    form = RegistrationForm(request.form)
    if form.validate():
        existing_user = users.find_one({'email': form.email.data})
        if existing_user:
            return jsonify({"error": "Email already registered"}), 400
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        users.insert_one({'username': form.username.data, 'email': form.email.data, 'password': hashed_password})
        return jsonify({"message": "Registered successfully"}), 201
    else:
        return jsonify({"error": form.errors}), 400



@app.route('/login', methods=['GET'])
def login_page():
    return app.send_static_file('login.html')


@app.route('/api/login', methods=['POST'])
@limiter.limit("10 per day")
def login():
    form = RegistrationForm(request.form)
    if form.validate():
        user = users.find_one({'username': form.username.data})
        if not user or not check_password_hash(user['password'], form.password.data):
            return jsonify({"error": "Invalid username or password"}), 401
        session['logged_in'] = True
        session['username'] = form.username.data
        return jsonify({"message": "Logged in successfully"}), 200
    else:
        return jsonify({"error": form.errors}), 400


@app.route('/logout', methods=['GET'])
def logout_page():
    return app.send_static_file('logout.html')


@app.route('/api/logout', methods=['POST'])
@limiter.limit("10 per day")
def logout():
    session['logged_in'] = False
    session.pop('username', None)
    return jsonify({"message": "Logged out successfully"}), 200


@app.route('/dashboard', methods=['GET'])
def dashboard_page():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login_page'))
    return app.send_static_file('dashboard.html')


@app.route('/task', methods=['POST'])
@limiter.limit("50 per day")
def create_task():
    if 'logged_in' not in session or not session['logged_in']:
        return jsonify({"error": "Please log in first"}), 401
    data = request.get_json()
    task_id = tasks.insert_one(data).inserted_id
    return jsonify(str(task_id)), 201


@app.route('/task', methods=['GET'])
@limiter.limit("100 per day")
def get_tasks():
    if 'logged_in' not in session or not session['logged_in']:
        return jsonify({"error": "Please log in first"}), 401
    task_list = list(tasks.find())
    for task in task_list:
        task["_id"] = str(task["_id"])
    return jsonify(task_list), 200


@app.route('/task/<id>', methods=['GET'])
@limiter.limit("50 per day")
def get_task(id):
    if 'logged_in' not in session or not session['logged_in']:
        return jsonify({"error": "Please log in first"}), 401
    task = tasks.find_one({'_id': ObjectId(id)})
    if task:
        task["_id"] = str(task["_id"])
        return jsonify(task), 200
    else:
        return jsonify({"error": "Task not found"}), 404


@app.route('/task/<id>', methods=['PUT'])
@limiter.limit("50 per day")
def update_task(id):
    if 'logged_in' not in session or not session['logged_in']:
        return jsonify({"error": "Please log in first"}), 401
    data = request.get_json()
    tasks.find_one_and_update({'_id': ObjectId(id)}, {'$set': data})
    return jsonify({"message": "Task updated successfully"}), 200


@app.route('/task/<id>', methods=['DELETE'])
@limiter.limit("50 per day")
def delete_task(id):
    if 'logged_in' not in session or not session['logged_in']:
        return jsonify({"error": "Please log in first"}), 401
    tasks.delete_one({'_id': ObjectId(id)})
    return jsonify({"message": "Task deleted successfully"}), 200


if __name__ == '__main__':
    app.run(debug=True)
