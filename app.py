from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_pymongo import PyMongo
from bcrypt import hashpw, gensalt, checkpw
from bson.objectid import ObjectId
from validate_email import validate_email
from flask_login import UserMixin
import script 
from flask_login import current_user
from bson.objectid import ObjectId


app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/myhosts"
app.secret_key = 'your_secret_key_here'

mongo = PyMongo(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_json):
        self.user_json = user_json

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.user_json['_id'])



@login_manager.user_loader
def load_user(user_id):
    u = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not u:
        return None
    return User(u)

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = mongo.db.users.find_one({"$or": [{"email": request.form.get('email')}, {"username": request.form.get('email')}]})
        if user and checkpw(request.form.get('password').encode('utf-8'), user['password']):
            user_obj = User(user)
            login_user(user_obj)
            if user_obj.user_json.get('admin'):  # Check if the user is an admin
                return redirect(url_for('admin'))  # Redirect to the admin dashboard
            else:
                return redirect(url_for('dashboard'))  # Redirect to the normal dashboard
    return render_template('login.html')

@app.route('/admin')
@login_required
def admin():
    if not current_user.user_json.get('admin'):
        return "You are not an admin!", 403
    users = mongo.db.users.find()
    return render_template('admin.html', users=users)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    apps = mongo.db.apps.find({"user_id": current_user.get_id()})
    return render_template('dashboard.html', apps=apps)



from flask import jsonify

import json
import requests

# @app.route('/create-app', methods=['GET', 'POST'])
# @login_required
# def create_app():
#     if request.method == 'POST':
#         name = request.form.get('name')
#         app_type = request.form.get('type')

#         # Check if the name or type is not provided
#         if not name or not app_type:
#             flash("App name and type are required!", 'error')
#             return redirect(url_for('create_app'))

#         # Check if the app name is already in use
#         existing_app = mongo.db.apps.find_one({"name": name})

#         if existing_app:
#             flash("App name already exists!", 'error')
#             return redirect(url_for('create_app'))

#         # Execute the /create-container endpoint
#         endpoint = "http://127.0.0.1:5000/create-container"
#         payload = {
#             "container": name,
#             "type": app_type
#         }

#         try:
#             response = requests.post(endpoint, json=payload)
#             response_data = response.json()
#             output = response_data.get('message')

#             # Insert the new app into the database
#             mongo.db.apps.insert_one({
#                 "name": name,
#                 "type": app_type,
#                 "user_id": current_user.get_id()  # associate the app with the current user
#             })

#             flash("App successfully created!", 'success')
#             return redirect(url_for('dashboard'))

#         except (requests.exceptions.RequestException, json.JSONDecodeError):
#             flash("Failed to create the app. Please try again.", 'error')
#             return redirect(url_for('create_app'))

#     # If it's a GET request, render the form
#     return render_template('create_app.html')
# Define the list of ports to be excluded

from random import randint


@app.route('/create-app', methods=['GET', 'POST'])
@login_required
def create_app():
    if request.method == 'POST':
        name = request.form.get('name')
        app_type = request.form.get('type')

        # Check if the name or type is not provided
        if not name or not app_type:
            flash("App name and type are required!", 'error')
            return redirect(url_for('create_app'))

        # Check if the app name is already in use
        existing_app = mongo.db.apps.find_one({"name": name})

        if existing_app:
            flash("App name already exists!", 'error')
            return redirect(url_for('create_app'))

        # Generate random port numbers, excluding reserved ports
        reserved_ports = [22, 80, 443, 21, 25, 53, 67, 68, 3389]
        port_number = randint(1000, 10000)
        while port_number in reserved_ports:
            port_number = randint(1000, 10000)

        second_port = randint(1000, 10000)
        while second_port == port_number or second_port in reserved_ports:
            second_port = randint(1000, 10000)

        ssh_port = randint(1000, 10000)
        while ssh_port == port_number or ssh_port == second_port or ssh_port in reserved_ports:
            ssh_port = randint(1000, 10000)

        # Call the create_container function
        output = script.create_container(name, app_type, port_number, second_port, ssh_port)

        if output:
            flash("App successfully created!", 'success')
            # Insert the new app with generated ports into the database
            mongo.db.apps.insert_one({
                "name": name,
                "type": app_type,
                "port_number": port_number,
                "second_port": second_port,
                "ssh_port": ssh_port,
                "user_id": current_user.get_id()  # associate the app with the current user
            })
        else:
            flash("Failed to create the app. Please try again.", 'error')
            output = "Failed to create the app."  # Assign a default output message

        # Pass the output to the template
        return render_template('create_app.html', output=output)

    # If it's a GET request, render the form
    return render_template('create_app.html')










from script import get_link

@app.route('/get-app-url/<id>', methods=['GET'])
@login_required
def get_app_url(id):
    # Retrieve the app details from the database using the app id
    app = mongo.db.apps.find_one({"_id": ObjectId(id)})

    if app:
        # Use the app name as the container name
        app_url = script.get_link(app['name'])
        # Return the app URL
        return render_template('app_url.html', app_url=app_url)
    else:
        flash("App not found!", 'error')
        return redirect(url_for('apps'))


@app.context_processor
def make_util_functions_available_to_template():
    return dict(get_link=get_link)

@app.route('/apps')
@login_required
def get_apps():
    if not current_user.user_json.get('admin'):
        return "You are not an admin!", 403
    apps = mongo.db.apps.find()  # Fetch all apps from the database
    return render_template('apps.html', apps=apps)


# @app.route('/apps', endpoint='apps')
# @login_required
# def get_apps():
#     # Check if the user is an admin
#     if not current_user.user_json.get('admin'):
#         return "You are not an admin!", 403

#     # Retrieve the apps from the database
#     apps = mongo.db.apps.find()

#     # Render the apps.html template with the apps
#     return render_template('apps.html', apps=apps)













# @app.route('/update-app/<id>', methods=['POST', 'GET'])
# def update_app(id):
#     if request.method == 'POST':
#         if 'action' in request.form:
#             app = mongo.db.apps.find_one({"_id": ObjectId(id)})
#             container_name = app['name']  # assuming 'name' corresponds to the docker container name

#             if request.form.get('action') == 'Check':
#                 is_running = script.check_container(container_name)
#                 flash(f"App is {'running' if is_running else 'not running'}!", 'success' if is_running else 'danger')
#             elif request.form.get('action') == 'Stop':
#                 script.stop_container(container_name)
#                 flash("App successfully stopped!", 'success')
#             elif request.form.get('action') == 'Start':
#                 script.start_container(container_name)
#                 flash("App successfully started!", 'success')
#         else:
#             name = request.form.get('name')
#             app_type = request.form.get('type')

#             # Check if the name or type is not provided
#             if not name or not app_type:
#                 flash("App name and type are required!")
#                 return render_template('update.html', id=id)

#             # Update the app in the database
#             mongo.db.apps.update_one({"_id": ObjectId(id)}, {"$set": {"name": name, "type": app_type}})
#             flash("App successfully updated!")
    
#     app = mongo.db.apps.find_one({"_id": ObjectId(id)})
#     return render_template('update.html', app=app) 



@app.route('/update-app/<id>', methods=['POST', 'GET'])
def update_app(id):
    if request.method == 'POST':
        if 'action' in request.form:
            app = mongo.db.apps.find_one({"_id": ObjectId(id)})
            container_name = app['name']  # assuming 'name' corresponds to the docker container name

            if request.form.get('action') == 'Check':
                is_running = script.check_container(container_name)
                flash(f"App is {'running' if is_running else 'not running'}!", 'success' if is_running else 'danger')
            elif request.form.get('action') == 'Stop':
                script.stop_container(container_name)
                flash("App successfully stopped!", 'success')
            elif request.form.get('action') == 'Start':
                script.start_container(container_name)
                flash("App successfully started!", 'success')
        else:
            name = request.form.get('name')
            app_type = request.form.get('type')

            # Check if the name or type is not provided
            if not name or not app_type:
                flash("App name and type are required!")
                return render_template('update.html', id=id)

            # Update the app in the database
            mongo.db.apps.update_one({"_id": ObjectId(id)}, {"$set": {"name": name, "type": app_type}})
            flash("App successfully updated!")
    
    app = mongo.db.apps.find_one({"_id": ObjectId(id)})
    return render_template('update.html', app=app)




@app.route('/delete-app/<id>', methods=['POST'])
def delete_app(id):
    # Check if the provided password matches the user's password
    password = request.form.get('password')
    user = mongo.db.users.find_one({"_id": ObjectId(current_user.get_id())})
    if not user or not checkpw(password.encode('utf-8'), user['password']):
        flash("Incorrect password!")
        return redirect(url_for('dashboard'))

    # Get the app from the database
    app = mongo.db.apps.find_one({"_id": ObjectId(id)})
    if not app:
        flash("App not found!")
        return redirect(url_for('dashboard'))

    # Stop and remove the docker container of the app
    script.delete_container(app['name'])

    # Delete the app from the database
    mongo.db.apps.delete_one({"_id": ObjectId(id)})

    flash("App successfully deleted!")
    return redirect(url_for('dashboard'))


@app.route('/get-app/<id>', methods=['GET', 'POST', 'PUT'])
def get_app(id):
    app = mongo.db.apps.find_one({"_id": ObjectId(id)})
    return render_template('update-app.html', app=app)




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        username = request.form.get('username')

        if not password == confirm_password:
            flash("Passwords do not match!")
            return redirect(url_for('register'))

        if not validate_email(email):
            flash("Invalid email!")
            return redirect(url_for('register'))

        existing_user = mongo.db.users.find_one({"email": email})

        if existing_user:
            flash("Email already in use!")
            return redirect(url_for('register'))

        existing_username = mongo.db.users.find_one({"username": username})

        if existing_username:
            flash("Username already in use!")
            return redirect(url_for('register'))

        hashpass = hashpw(password.encode('utf-8'), gensalt())
        mongo.db.users.insert_one({
            "email": email,
            "password": hashpass,
            "username": username
        })
        return redirect(url_for('login'))

    return render_template('register.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

