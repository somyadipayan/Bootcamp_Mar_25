from flask import Flask, jsonify, request, Response, send_file
from models import *
from config import Config
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, unset_jwt_cookies
from tools import workers, tasks, mailer
import csv, io
import matplotlib.pyplot as plt
import base64
from flask_caching import Cache


app = Flask(__name__)
app.config.from_object(Config)

# Initializing objects in app context
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)
mailer.init_app(app)
cache = Cache(app)
celery = workers.celery
celery.conf.update(
    broker_url=app.config['CELERY_BROKER_URL'],
    result_backend=app.config['CELERY_RESULT_BACKEND']
)

celery.Task = workers.ContextTask

CORS(app, supports_credentials=True)

app.app_context().push()

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
    tasks.add.delay(41, 32)
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

# CRUD ON CATEGORY

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
    
    print(name)

    if not name:
        return jsonify({"error": "Required Fields are empty"}), 400


    existing_category = Category.query.filter_by(name=name).first()
    if existing_category:
        return jsonify({"error": f"Category {name} already exists"}), 400



    try:
        new_category = Category(name=name)
        db.session.add(new_category)
        db.session.commit()
        return jsonify({"message": f"Category {name} created"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 500

# READ ALL CATEGORIES

@app.route("/categories", methods=["GET"])
@cache.cached(timeout=600)
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

# READ A SINGLE CATEGORY
@app.route("/category/<int:category_id>", methods=["GET"])
def read_category(category_id):
    category = Category.query.filter_by(id=category_id).first()
    products = []
    for product in category.products:
        products.append({
            "id":product.id,
            "name":product.name,
            "unit":product.unit,
            "price":product.price,
            "quantity":product.quantity,
        })
    category_data = {
        "id": category.id,
        "name": category.name,
        "products": products    
    }
    return jsonify(category_data), 200

# Update a Category # Managers and Admins
@app.route("/category/<int:category_id>", methods=["PUT"])
@jwt_required()
def update_category(category_id):
    this_user = get_jwt_identity()
    if this_user["role"] not in ["manager", "admin"]:
        return jsonify({"error": "You are not authorized to perform this action"}), 403

    category = Category.query.filter_by(id=category_id).first()
    if not category:
        return jsonify({"error": "Category not found"}), 404

    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"error": "Required Fields are empty"}), 400

    try:
        category.name = name
        db.session.commit()
        return jsonify({"message": f"Category {name} updated"}), 200

    except Exception as e:
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 500

# Delete a Category # Managers and Admins
@app.route("/category/<int:category_id>", methods=["DELETE"])
@jwt_required()
def delete_category(category_id):
    this_user = get_jwt_identity()
    if this_user["role"] not in ["manager", "admin"]:
        return jsonify({"error": "You are not authorized to perform this action"}), 403

    category = Category.query.filter_by(id=category_id).first()

    if not category:
        return jsonify({"error": "Category not found"}), 404

    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({"message": f"Category {category.name} deleted"}), 200

    except Exception as e:
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 500
    
# CRUD ON PRODUCT
# ONLY MANAGER

# Create a Product
@app.route("/product", methods=["POST"])
@jwt_required()
def create_product():
    this_user = get_jwt_identity()
    if this_user["role"] != "manager":
        return jsonify({"error": "You are not authorized to perform this action"}), 403

    data = request.get_json()
    name = data.get("name")
    unit = data.get("unit")
    price = data.get("price")
    quantity = data.get("quantity")
    category_id = data.get("category_id")
    creator_id = this_user["id"]

    if not name or not unit or not price or not quantity or not category_id:
        return jsonify({"error": "Required Fields are empty"}), 400

    category = Category.query.filter_by(id=category_id).first()
    if not category:
        return jsonify({"error": "Category not found"}), 404
    
    existing_product = Product.query.filter_by(name=name, category_id=category_id).first()
    if existing_product:
        return jsonify({"error": f"Product {name} already exists"}), 400

    try:
        new_product = Product(name=name,
                              unit=unit,
                              price=price,
                              quantity=quantity,
                              category_id=category_id,
                              creator_id=creator_id)
        db.session.add(new_product)
        db.session.commit()
        return jsonify({"message": f"Product {name} created"}), 200
    except Exception as e:
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 500

# READ ALL PRODUCTS IN A CATEGORY
@app.route("/products", methods=["GET"])
def read_products():
    data = request.get_json()
    category_id = data.get("category_id")
    products = Product.query.filter_by(category_id=category_id).all()
    products_data = []
    for product in products:
        products_data.append({
            "id":product.id,
            "name":product.name,
            "unit":product.unit,
            "price":product.price,
            "quantity":product.quantity,
        })
    return jsonify({
        "products": products_data
    }), 200

# READ A SINGLE PRODUCT
@app.route("/product/<int:product_id>", methods=["GET"])
def read_product(product_id):
    product = Product.query.filter_by(id=product_id).first()
    product_data = {
        "id": product.id,
        "name": product.name,
        "unit": product.unit,
        "price": product.price,
        "quantity": product.quantity,
    }
    return jsonify(product_data), 200

# UPDATE A PRODUCT
@app.route("/product/<int:product_id>", methods=["PUT"])
@jwt_required()
def update_product(product_id):
    this_user = get_jwt_identity()
    if this_user["role"] != "manager":
        return jsonify({"error": "You are not authorized to perform this action"}), 403

    product = Product.query.filter_by(id=product_id).first()
    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json()
    name = data.get("name")
    unit = data.get("unit")
    price = data.get("price")
    quantity = data.get("quantity")

    if not name or not unit or not price or not quantity:
        return jsonify({"error": "Required Fields are empty"}), 400
    
    existing_product = Product.query.filter_by(name=name).first()

    if existing_product and existing_product.id != product_id:
        return jsonify({"error": f"Product {name} already exists"}), 400
    
    try:
        product.name = name
        product.unit = unit
        product.price = price
        product.quantity = quantity
        db.session.commit()
        return jsonify({"message": f"Product {name} updated"}), 200
    except Exception as e:
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 500
    
# DELETE A PRODUCT
@app.route("/product/<int:product_id>", methods=["DELETE"])
@jwt_required()
def delete_product(product_id):
    this_user = get_jwt_identity()
    if this_user["role"] != "manager":
        return jsonify({"error": "You are not authorized to perform this action"}), 401

    product = Product.query.filter_by(id=product_id).first()

    if not product:
        return jsonify({"error": "Product not found"}), 404

    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": f"Product {product.name} deleted"}), 200

    except Exception as e:
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 500

@app.route("/add-to-cart", methods=["POST"])
@jwt_required()
def add_to_cart():
    this_user = get_jwt_identity()
    if this_user["role"] != "user":
        return jsonify({"error": "You are not authorized to perform this action"}), 401
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity")

    if not product_id or not quantity:
        return jsonify({"error": "Required Fields are empty"}), 400

    if quantity < 1:
        return jsonify({"error": "Quantity must be greater than 0"}), 400

    product = Product.query.filter_by(id=product_id).first()

    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    if product.quantity < quantity:
        return jsonify({"error": "Not enough quantity available"}), 400

    
    user_cart = ShoppingCart.query.filter_by(user_id=this_user["id"]).first()
    if not user_cart:
        user_cart = ShoppingCart(user_id=this_user["id"])
        try:
            db.session.add(user_cart)
            db.session.commit()
        except Exception as e: 
            return jsonify({"error": f"Failed to add to cart: {str(e)}"}), 500
        
    cart_item = CartItems.query.filter_by(product_id=product_id, cart_id=user_cart.id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItems(product_id=product_id, quantity=quantity, cart_id=user_cart.id)
        db.session.add(cart_item)
    try:
        db.session.commit()
        return jsonify({"message": f"Added {quantity} {product.name} to cart"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to add to cart: {str(e)}"}), 500

# VIEW THE CART - GET 
# REMOVE FROM CART - DELETE
# UPDATE THE CART - PUT

@app.route("/view-cart", methods=["GET"])
@jwt_required()
def view_cart():
    this_user = get_jwt_identity()
    if this_user["role"] != "user":
        return jsonify({"error": "You are not authorized to perform this action"}), 401

    user_cart = ShoppingCart.query.filter_by(user_id=this_user["id"]).first()

    if not user_cart or not user_cart.cart_items:
        return jsonify({"message": "Cart is empty"}), 200

    cart_items = []
    total_amount = 0.0
    for item in user_cart.cart_items:
        product = Product.query.get(item.product_id)
        if product:
            item_total = product.price * item.quantity
            total_amount += item_total
            cart_items.append({
                "item_id": item.id,
                "product_id": product.id,
                "product_name": product.name,
                "unit_price": product.price,
                "quantity": item.quantity,
                "total": item_total,
                "unit": product.unit
            })

    return jsonify({
        "cart_items": cart_items,
        "total_amount": total_amount
    }), 200

@app.route("/remove-from-cart/<int:item_id>", methods=["DELETE"])
@jwt_required()
def remove_from_cart(item_id):
    this_user = get_jwt_identity()
    if this_user["role"] != "user":
        return jsonify({"error": "You are not authorized to perform this action"}), 401

    cart_item = CartItems.query.get(item_id)
    if not cart_item:
        return jsonify({"error": "Cart item not found"}), 404

    user_cart = ShoppingCart.query.filter_by(user_id=this_user["id"]).first()
    if not user_cart or cart_item.cart_id != user_cart.id:
        return jsonify({"error": "Item not in your cart"}), 403

    try:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({"message": "Item removed from cart successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to remove item: {str(e)}"}), 500

@app.route("/update-cart/<int:item_id>", methods=["PUT"])
@jwt_required()
def update_cart(item_id):
    this_user = get_jwt_identity()
    if this_user["role"] != "user":
        return jsonify({"error": "You are not authorized to perform this action"}), 401

    data = request.get_json()
    new_quantity = data.get("quantity")

    if not new_quantity or new_quantity < 0:
        return jsonify({"error": "Invalid quantity"}), 400

    cart_item = CartItems.query.get(item_id)
    if not cart_item:
        return jsonify({"error": "Cart item not found"}), 404

    user_cart = ShoppingCart.query.filter_by(user_id=this_user["id"]).first()
    if not user_cart or cart_item.cart_id != user_cart.id:
        return jsonify({"error": "Item not in your cart"}), 403

    product = Product.query.get(cart_item.product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    if new_quantity > product.quantity:
        return jsonify({"error": "Requested quantity exceeds available stock"}), 400

    try:
        if new_quantity == 0:
            db.session.delete(cart_item)
        else:
            cart_item.quantity = new_quantity
        db.session.commit()
        return jsonify({"message": "Cart updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update cart: {str(e)}"}), 500



@app.route("/place-order", methods=["POST"])
@jwt_required()
def place_order():
    this_user = get_jwt_identity()
    if this_user["role"] != "user":
        return jsonify({"error": "You are not authorized to perform this action"}), 401
    
    user_cart = ShoppingCart.query.filter_by(user_id=this_user["id"]).first()

    if not user_cart or not user_cart.cart_items:
        return jsonify({"error": "Cart is empty"}), 400

    order_items = []
    total_amount = 0
    for item in user_cart.cart_items:
        if item.quantity > item.product.quantity:
            return jsonify({"error": f"Not enough quantity of {item.product.name} available"}), 400

        item.product.quantity -= item.quantity
        total_amount += item.product.price * item.quantity

        order_item = OrderItems(product_id=item.product_id, quantity=item.quantity)
        order_items.append(order_item)
    new_order = Order(user_id=this_user["id"], total_amount=total_amount, order_items=order_items)
    try:
        db.session.add(new_order)
        db.session.delete(user_cart)
        db.session.commit()
        return jsonify({"message": "Order placed successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to place order: {str(e)}"}), 500

@app.route("/get-orders", methods=["GET"])
@jwt_required()
def get_orders():
    this_user = get_jwt_identity()
    if this_user["role"] != "user":
        return jsonify({"error": "You are not authorized to perform this action"}), 401

    orders = Order.query.filter_by(user_id=this_user["id"]).order_by(Order.order_date.desc()).all()

    orders_data = []
    for order in orders:
        order_data = {
            "id": order.id,
            "date": order.order_date.strftime("%Y-%m-%d %H:%M:%S"),
            "total": order.total_amount,
            "items": []
        }
        for item in order.order_items:
            product = Product.query.get(item.product_id)
            if product:
                order_data["items"].append({
                    "product_id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "quantity": item.quantity,
                    "subtotal": product.price * item.quantity
                })
        orders_data.append(order_data)

    return jsonify({"orders": orders_data}), 200

#GENERATE CSV REPORT FOR ADMIN

def generate_report():
    orders = Order.query.all()
    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer)

    csv_writer.writerow(["Order ID", "User", "Order Date", "Total Amount"])
    for order in orders:
        csv_writer.writerow([order.id, order.user.username, order.order_date.strftime("%Y-%m-%d %H:%M:%S"), order.total_amount])

    return csv_buffer.getvalue()

@app.route("/download-order-csv", methods=["GET"])
def download_order_csv():
    csv_data = generate_report()
    return Response(csv_data, mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=order_report.csv"}), 200

# Order History
@app.route('/order-history-report', methods=['GET'])
def order_history_report():
    orders = Order.query.all()
    total_orders = len(orders)
    total_amount = sum(order.total_amount for order in orders)
    total_items = sum(item.quantity for order in orders for item in order.order_items)

    # Bar chart - X axis - date Y axis - Count of orders

    order_dates = [order.order_date.strftime('%Y-%m-%d') for order in orders]
    order_counts = {date: order_dates.count(date) for date in set(order_dates)}
    
    plt.figure(figsize=(10, 6))
    plt.bar(order_counts.keys(), order_counts.values())
    plt.xlabel('Date')
    plt.ylabel('Number of Orders')
    plt.title('Order History Report')
    plt.xticks(rotation=45)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    return jsonify({
        'total_orders': total_orders,
        'total_amount': total_amount,
        'total_items': total_items,
        'order_counts': order_counts,
    })

@app.route('/order-history-report-graph', methods=['GET'])
def order_history_report_graph():
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return send_file(img, mimetype='image/png')


@app.route('/order-category-pie-chart', methods=['GET'])
def order_category_pie_chart():

    orders = Order.query.all()

    category_counts = {}
    for order in orders:
        for item in order.order_items:
            category_name = item.product.category.name
            if category_name not in category_counts:
                category_counts[category_name] = 0
            category_counts[category_name] += item.quantity

    plt.figure(figsize=(10, 6))
    plt.pie(category_counts.values(), labels=category_counts.keys(), autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Orders from Different Categories')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    return send_file(img, mimetype='image/png')
  
if __name__ == "__main__":
    app.run(debug=True)