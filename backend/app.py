from flask import Flask, jsonify, request
from models import *
from config import Config
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, unset_jwt_cookies


app = Flask(__name__)
app.config.from_object(Config)

# Initializing objects in app context
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

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
    
# LOGIN
@app.route("/login", methods=["POST"])
def login():
   # Getting JSON from request
   data = request.get_json()
   # Getting user details from JSON
   username = data.get("username")
   password = data.get("password")

   # Checking if all fields are present
   if not username or not password:
       return jsonify({"error": "All fields are required"}), 400
   # Check if username and password don't match to our DB
   user = User.query.filter_by(username=username).first()

   # if user is not there or password doesn't match
   if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Invalid username or password"}), 401

   # Create JWT token
   access_token = create_access_token(identity={
       "id": user.id,
       "username": user.username,
       "role": user.role
   })

   # Update the last logged in time
   user.lastLoggedIn = datetime.now()
   db.session.commit()
       
   return jsonify({"message": "Login successful", "access_token": access_token}), 200

@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    return jsonify({"message": "Protected route accessed successfully"}), 200


# ONLY ADMINS CAN ACCESS THIS AREA 51
@app.route("/area-51", methods=["GET"])
@jwt_required()
def area51():
    this_user = get_jwt_identity()
    if this_user["role"] != "admin":
        return jsonify({"error": "Unauthorized access"}), 403
    return jsonify({"message": "Area 51 accessed successfully"}), 200

@app.route("/getuserinfo", methods=["GET"])
@jwt_required()
def get_user_info():
    this_user = get_jwt_identity()
    try:
        user = User.query.filter_by(id=this_user["id"]).first()
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "lastLoggedIn": user.lastLoggedIn
        }
        return jsonify(user_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response


# CREATE A CATEGORY
@app.route("/category", methods=["POST"])
@jwt_required()
def create_category():
    # ONLY MANAGERS AND ADMINS CAN CREATE CATEGORIES
    this_user = get_jwt_identity()
    if this_user["role"] not in ["manager", "admin"]:
        return jsonify({"error": "You are not authorized to perform this action"}), 403

    # Getting JSON from request
    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"error": "Required Fields are empty"}), 400


    existing_category = Category.query.filter_by(name=name).first()
    if existing_category:
        return jsonify({"error": f"Category {name} already exists"}), 400

    try:
        new_category = Category(name=name)
        db.session.add(new_category)
        db.session.commit()
        return jsonify({"message": f"Category {name} created"}), 400
        
    except Exception as e:
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 500

# READ ALL CATEGORIES
@app.route("/categories", methods=["GET"])
def read_categories():
    categories = Category.query.all()
    categories_data = []
    for category in categories:
        products = []
        for product in category.products:
            products.append({
                "id":product.id,
                "name":product.name,
                "unit":product.unit,
                "price":product.price,
                "quantity":product.quantity,
            })
        categories_data.append(
            {
                "id": category.id,
                "name": category.name,
                "products": products
            }
        )
    return jsonify(categories_data)

if __name__ == "__main__":
    app.run(debug=True)