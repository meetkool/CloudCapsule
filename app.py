import os
import re
import logging
from flask import Flask, render_template, redirect, request, flash, send_from_directory , jsonify
from flask_pymongo import PyMongo
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
import shutil
import zipfile
from pathlib import Path


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/your_database'
app.config['WEBSITES_FOLDER'] = 'websites'
mongo = PyMongo(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Setting up logging
logging.basicConfig(filename='app.log', level=logging.INFO)

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.username = user_data["username"]
        self.email = user_data["email"]

@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

class HostingApplication:
    def __init__(self, app_data):
        self.id = str(app_data["_id"])
        self.name = app_data["name"]
        self.domain = app_data["domain"]
        self.plan = app_data["plan"]
        self.user_id = app_data["user_id"]
        self.website_id = app_data.get("website_id", None)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        existing_user = mongo.db.users.find_one({"$or": [{"username": username}, {"email": email}]})
        if existing_user:
            flash("Username or email already exists.", "error")
            return redirect("/register")

        email_pattern = re.compile(r'^[\w.-]+@[\w.-]+\.\w+$')
        if not email_pattern.match(email):
            flash("Invalid email address.", "error")
            return redirect("/register")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect("/register")

        hashed_password = generate_password_hash(password)
        user_data = {"username": username, "email": email, "password": hashed_password}
        user_id = mongo.db.users.insert_one(user_data).inserted_id
        user = User(user_data)
        login_user(user)

        logging.info(f'New user registered: {username}')
        return redirect("/dashboard")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email_or_username = request.form["email_or_username"]
        password = request.form["password"]

        user_data = mongo.db.users.find_one(
            {"$or": [{"username": email_or_username}, {"email": email_or_username}]})
        if user_data and check_password_hash(user_data["password"], password):
            user = User(user_data)
            login_user(user)
            logging.info(f'Successfully logged in user: {user.username}')
            logging.info(f'User is authenticated: {current_user.is_authenticated}')
            return redirect("/dashboard")

        flash("Invalid email/username or password.", "error")
        return redirect("/login")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    logging.info('User logged out')
    return redirect("/")


@app.route("/dashboard")
@login_required
def dashboard():
    user_apps_data = mongo.db.apps.find({"user_id": current_user.id})
    user_apps = [HostingApplication(app) for app in user_apps_data]
    return render_template("dashboard.html", user_apps=user_apps)


@app.route("/apps/create", methods=["GET", "POST"])
@login_required
def create_app():
    if request.method == "POST":
        name = request.form["name"]
        domain = request.form["domain"]
        plan = request.form["plan"]
        website_file = request.files["website_file"]

        user_folder = os.path.join(app.config['WEBSITES_FOLDER'], str(current_user.id))
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        website_id = str(ObjectId())
        filename = secure_filename(website_file.filename)
        website_path = os.path.join(user_folder, website_id)
        os.makedirs(website_path)
        website_file.save(os.path.join(website_path, filename))

        app_data = {
            "name": name,
            "domain": domain,
            "plan": plan,
            "user_id": current_user.id,
            "website_id": website_id
        }
        app_id = mongo.db.apps.insert_one(app_data).inserted_id

        flash("Hosting application created successfully!", "success")
        return redirect("/dashboard")

    return render_template("create_app.html")



@app.route("/apps/<app_id>/delete", methods=["POST"])
@login_required
def delete_app(app_id):
    mongo.db.apps.delete_one({"_id": ObjectId(app_id)})
    flash("Hosting application deleted successfully!", "success")
    return redirect("/dashboard")
    
@app.route("/apps/<app_id>")
@login_required
def app_details(app_id):
    app_data = mongo.db.apps.find_one({"_id": ObjectId(app_id)})
    if not app_data:
        flash("Application not found.", "error")
        return redirect("/dashboard")

    app = HostingApplication(app_data)
    return render_template("app_details.html", app=app)

@app.route("/apps/<app_id>/edit", methods=["GET", "POST"])
@login_required
def edit_app(app_id):
    app_data = mongo.db.apps.find_one({"_id": ObjectId(app_id)})

    if not app_data:
        flash("Application not found.", "error")
        return redirect("/dashboard")

    hosting_app = HostingApplication(app_data)

    if request.method == "POST":
        name = request.form["name"]
        domain = request.form["domain"]
        plan = request.form["plan"]

        mongo.db.apps.update_one({"_id": ObjectId(app_id)}, {"$set": {"name": name, "domain": domain, "plan": plan}})

        flash("Application updated successfully!", "success")
        return redirect("/apps/" + app_id)

    # Get subfolder path
    subfolder = request.args.get("subfolder", "")
    current_subfolder = subfolder  # Initialize current_subfolder
    user_folder = os.path.join(app.config['WEBSITES_FOLDER'], str(current_user.id), app_data["website_id"], subfolder)

    # Compute the parent folder's path
    parent_folder = "/".join(subfolder.split("/")[:-1]) if subfolder else ""

    if os.path.exists(user_folder):
        files_and_folders = [{'name': name, 'type': 'folder' if os.path.isdir(os.path.join(user_folder, name)) else 'file'} for name in os.listdir(user_folder)]
    else:
        files_and_folders = []

    return render_template("edit_app.html", hosting_app=hosting_app, files=files_and_folders, current_subfolder=current_subfolder, parent_folder=parent_folder)



@app.route('/websites/<user_id>/<website_id>/<path:filename>')
def serve_website(user_id, website_id, filename):
    user_folder = os.path.join(app.config['WEBSITES_FOLDER'], user_id, website_id)
    return send_from_directory(user_folder, filename)


from flask import render_template_string

@app.route("/apps/<app_id>/upload", methods=['POST'])
@login_required
def upload_files(app_id):
    app_data = mongo.db.apps.find_one({"_id": ObjectId(app_id)})
    if not app_data:
        flash("Application not found.", "error")
        return redirect("/dashboard")

    # Check if the post request has the file part
    if 'website_file' not in request.files:
        flash('No file part', "error")
        return redirect("/apps/" + app_id + "/edit")
    
    file = request.files['website_file']
    
    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file', "error")
        return redirect("/apps/" + app_id + "/edit")
    
    allowed_extensions = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'html', 'js', 'css'])
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    if '.' in file.filename and file_extension not in allowed_extensions:
        flash('File extension not allowed!', 'error')
        return render_template_string('''
            <script>
                alert("File extension not allowed!");
                window.location.href = "/apps/{{ app_id }}/edit";
            </script>
        ''', app_id=app_id)
    
    filename = secure_filename(file.filename)
    user_folder = os.path.join(app.config['WEBSITES_FOLDER'], str(current_user.id), app_data["website_id"])
    file.save(os.path.join(user_folder, filename))
    
    flash('File successfully uploaded', "success")
    return redirect("/apps/" + app_id + "/edit")

    filename = secure_filename(file.filename)
    user_folder = os.path.join(app.config['WEBSITES_FOLDER'], str(current_user.id), app_data["website_id"])
    file.save(os.path.join(user_folder, filename))
    
    flash('File successfully uploaded', "success")
    return redirect("/apps/" + app_id + "/edit")



@app.route("/apps/<app_id>/files")
@login_required
def view_files(app_id):
    app_data = mongo.db.apps.find_one({"_id": ObjectId(app_id)})
    if not app_data:
        flash("Application not found.", "error")
        return redirect("/dashboard")

    user_folder = os.path.join(app.config['WEBSITES_FOLDER'], str(current_user.id), app_data["website_id"])
    files = os.listdir(user_folder) if os.path.exists(user_folder) else []
    return render_template("view_files.html", files=files, app_id=app_id)

@app.route("/apps/<app_id>/create-folder", methods=['POST'])
@login_required
def create_folder(app_id):
    app_data = mongo.db.apps.find_one({"_id": ObjectId(app_id)})
    if not app_data:
        flash("Application not found.", "error")
        return redirect("/dashboard")

    folder_name = request.form['folder_name']
    user_folder = os.path.join(app.config['WEBSITES_FOLDER'], str(current_user.id), app_data["website_id"], folder_name)
    
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
        flash('Folder created successfully', "success")
    else:
        flash('Folder already exists', "error")
        
    return redirect("/apps/" + app_id + "/edit")

@app.route("/apps/<app_id>/delete-file", methods=['GET'])
@login_required
def delete_file(app_id):
    app_data = mongo.db.apps.find_one({"_id": ObjectId(app_id)})
    if not app_data:
        flash("Application not found.", "error")
        return redirect("/dashboard")

    file = request.args.get('file')
    file_path = os.path.join(app.config['WEBSITES_FOLDER'], str(current_user.id), app_data["website_id"], file)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        flash('File deleted successfully', "success")
    else:
        flash('File not found', "error")

    return redirect("/apps/" + app_id + "/edit")

@app.route("/apps/<app_id>/upload-unzip", methods=['POST'])
@login_required
def upload_unzip(app_id):
    app_data = mongo.db.apps.find_one({"_id": ObjectId(app_id)})
    if not app_data:
        flash("Application not found.", "error")
        return redirect("/dashboard")

    if 'zip_file' not in request.files:
        flash('No file part', "error")
        return redirect("/apps/" + app_id + "/edit")
    
    file = request.files['zip_file']
    
    if file.filename == '':
        flash('No selected file', "error")
        return redirect("/apps/" + app_id + "/edit")
    
    if file.filename.endswith('.zip'):
        filename = secure_filename(file.filename)
        user_folder = os.path.join(app.config['WEBSITES_FOLDER'], str(current_user.id), app_data["website_id"])
        file.save(os.path.join(user_folder, filename))
        
        with zipfile.ZipFile(os.path.join(user_folder, filename), 'r') as zip_ref:
            zip_ref.extractall(user_folder)
        
        os.remove(os.path.join(user_folder, filename))
        flash('Zip file uploaded and unzipped successfully', "success")
    else:
        flash('File is not a zip file', "error")

    return redirect("/apps/" + app_id + "/edit")

@app.route('/apps/<app_id>/get-file', methods=['GET'])
def get_file(app_id):
    filename = request.args.get('file')
    app_data = mongo.db.apps.find_one({"_id": ObjectId(app_id)})
    user_folder = os.path.join(app.config['WEBSITES_FOLDER'], str(current_user.id), app_data["website_id"])
    file_path = os.path.join(user_folder, filename)

    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        return jsonify({'content': content})
    else:
        flash('File not found', "error")
        return jsonify({'error': 'File not found'})

@app.route('/apps/<app_id>/save-file', methods=['POST'])
def save_file(app_id):
    filename = request.form.get('filename')
    content = request.form.get('content')
    app_data = mongo.db.apps.find_one({"_id": ObjectId(app_id)})
    user_folder = os.path.join(app.config['WEBSITES_FOLDER'], str(current_user.id), app_data["website_id"])
    file_path = os.path.join(user_folder, filename)

    if os.path.isfile(file_path):
        with open(file_path, 'w') as file:
            file.write(content)
        return jsonify({'message': 'File saved successfully'})
    else:
        flash('File not found', "error")
        return jsonify({'error': 'File not found'})



@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", error="Page not found."), 404

if __name__ == "__main__":
    app.run(debug=True)
