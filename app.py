from flask import Flask, render_template, redirect, request, flash
from flask_pymongo import PyMongo
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import re
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/your_database'
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

        app_data = {
            "name": name,
            "domain": domain,
            "plan": plan,
            "user_id": current_user.id
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

    if request.method == "POST":
        name = request.form["name"]
        domain = request.form["domain"]
        plan = request.form["plan"]

        mongo.db.apps.update_one({"_id": ObjectId(app_id)}, {"$set": {"name": name, "domain": domain, "plan": plan}})
        flash("Application updated successfully!", "success")
        return redirect("/apps/" + app_id)

    app = HostingApplication(app_data)
    return render_template("edit_app.html", app=app)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", error="Page not found."), 404


if __name__ == "__main__":
    app.run(debug=True)
