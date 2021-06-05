from . import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), unique=True, nullable=False)

class Book(db.Model):
    isbn = db.Column(db.String(13), primary_key=True)
    title = db.Column(db.String(), nullable=False)
    bookprice = db.Column(db.Numeric(6, 2), default=0.00)
    due_date = db.Column(db.Date, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    book_status = db.Column(db.Boolean, default=True)