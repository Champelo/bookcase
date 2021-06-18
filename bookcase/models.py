from . import db
from flask_login import UserMixin
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), unique=True, nullable=False)
    budget = db.Column(db.Numeric(6, 2), default=0.00)
    bud_remaining = db.Column(db.Numeric(6, 2), default=0.00)

class Book(db.Model):
    isbn = db.Column(db.String(13), primary_key=True)
    title = db.Column(db.String(), nullable=False)
    bookprice = db.Column(db.Numeric(6, 2), default=0.00)
    purchased_date = db.Column(db.Date, nullable=False, default=datetime.utcnow())
    due_date = db.Column(db.Date, nullable=True, default=None)
    status = db.Column(db.Boolean, default=True)
    overdue = db.Column(db.Boolean, default=False)
    borrower_id = db.Column(db.Integer, db.ForeignKey('borrower.borrowerId'))
    borrower = db.relationship('Borrower')
    

class Borrower(db.Model):
    borrowerId = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(), nullable=False)
    lname = db.Column(db.String(), nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=5)
    book = db.relationship('Book', back_populates='borrower')