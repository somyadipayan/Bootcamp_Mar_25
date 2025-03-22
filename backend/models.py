from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    lastLoggedIn = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __init__(self, username, email, role, password):
        self.username = username
        self.email = email
        self.role = role
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    # Relationship
    products = db.relationship('Product', back_populates='category', cascade="all, delete-orphan")

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False) # Piece, KG, Litre
    quantity = db.Column(db.Integer, nullable=False) # The amount of product in stock
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Relationships
    category = db.relationship('Category', back_populates='products')
    creator = db.relationship('User', backref='products')


# Every person will have a cart
class ShoppingCart(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Relationships
    user = db.relationship('User', backref='cart')
    cart_items = db.relationship('CartItems', back_populates='cart', cascade="all, delete-orphan")

# and each cart will have multiple items in multiple qtys
class CartItems(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    cart_id = db.Column(db.Integer, db.ForeignKey('shopping_cart.id'), nullable=False)
    # Relationships
    cart = db.relationship('ShoppingCart', back_populates='cart_items')
    product = db.relationship('Product', backref='cart_items')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    total_amount = db.Column(db.Float, nullable=False)
    # Relationships
    user = db.relationship('User', backref='orders')

class OrderItems(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    # Relationships
    order = db.relationship('Order', backref='order_items')
    product = db.relationship('Product', backref='order_items')