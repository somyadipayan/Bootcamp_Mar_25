from flask import Flask, jsonify, request
from models import *
from config import Config
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)

# Initializing objects in app context
db.init_app(app)
bcrypt.init_app(app)

CORS(app, supports_credentials=True)

def create_admin():
    existing_admin = User.query.filter_by(role='admin').first()
    if existing_admin:
        return jsonify({"message": "Admin already exists"}), 200
    try:
        admin = User(username="admin",
                     email="admin@store.com",
                     role="admin",
                     password=app.config['ADMIN_PASSWORD'])
        db.session.add(admin)
        db.session.commit()
        return jsonify({"message": "Admin created successfully"}), 201
    except Exception as e:
        return jsonify({"message": "Error creating admin", "error": str(e)}), 500
    

with app.app_context():
    db.create_all()
    create_admin()

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/register", methods=["POST"])
def register():
    
    # Getting JSON from request
    data = request.get_json()
    
    # Getting user details from JSON
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    # Checking if all fields are present
    if not username or not email or not password or not role:
        return jsonify({"error": "All fields are required"}), 400

    # Checking if user already exists
    existing_user = User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "User already exists"}), 400

    # Creating user
    try:
        user = User(username=username, email=email, role=role, password=password)
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


   
if __name__ == "__main__":
    app.run(debug=True)