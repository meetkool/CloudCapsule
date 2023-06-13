from pymongo import MongoClient
from bcrypt import hashpw, gensalt

def create_admin_user():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.myhosts
    users = db.users

    # Checking if an admin already exists
    existing_admin = users.find_one({"admin": True})

    if existing_admin is not None:
        print("Admin user already exists!")
        return

    password = "admin1234"  # Replace this with a strong password
    hashed_password = hashpw(password.encode('utf-8'), gensalt())

    # Inserting the admin user
    users.insert_one({
        "email": "admin@email.com",
        "password": hashed_password,
        "username": "admin",
        "admin": True
    })

    print("Admin user created successfully!")

if __name__ == "__main__":
    create_admin_user()
