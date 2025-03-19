# filepath: /Users/ihthishamibrahim/mp2/price-comparison-website/src/models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    # Add relationships
    wishlist = db.relationship('Wishlist', backref='user', lazy=True)
    price_alerts = db.relationship('PriceAlert', backref='user', lazy=True)

class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_name = db.Column(db.String(200))
    product_url = db.Column(db.String(500))
    current_price = db.Column(db.Float)
    added_date = db.Column(db.DateTime, default=datetime.utcnow)

class PriceAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_url = db.Column(db.String(500))
    target_price = db.Column(db.Float)
    current_price = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)

class PriceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_url = db.Column(db.String(500))
    price = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.utcnow)