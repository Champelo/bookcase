from . import db, ma
from flask_login import UserMixin
from datetime import datetime
from marshmallow import fields

booksauthors = db.Table('booksauthors',
                db.Column('author_id', db.Integer(), db.ForeignKey('author.id'), primary_key=True),
                db.Column('book_isbn', db.String(), db.ForeignKey('book.isbn'), primary_key=True))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), unique=True, nullable=False)
    budget = db.Column(db.Numeric(6, 2), default=0.00)
    bud_remaining = db.Column(db.Numeric(6, 2), default=0.00)

class Borrower(db.Model):
    borrowerId = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(), nullable=False)
    lname = db.Column(db.String(), nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=5)
class BorrowerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Borrower
        sqla_session = db.session

class Author(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), default='Unknown')
class AuthorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Author
        sqla_session = db.session
        include_fk = True

class Book(db.Model):
    isbn = db.Column(db.String(13), primary_key=True)
    title = db.Column(db.String(), nullable=False)
    bookprice = db.Column(db.Numeric(6, 2), default=0.00)
    purchased_date = db.Column(db.Date, nullable=False, default=datetime.utcnow())
    due_date = db.Column(db.Date, nullable=True, default=None)
    status = db.Column(db.Boolean, default=True)
    overdue = db.Column(db.Boolean, default=False)
    thumbnail = db.Column(db.String(), nullable=True, default='../../static/asset/images/freesia.svg')
    borrower_id = db.Column(db.Integer, db.ForeignKey('borrower.borrowerId'))
    authors = db.relationship('Author', secondary=booksauthors, lazy='subquery',
    backref=db.backref('books', lazy=True))
    borrower = db.relationship('Borrower', foreign_keys=borrower_id)
class BookSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Book
        sqla_session = db.session
        include_fk = True
    authors = fields.Nested("AuthorSchema", default=[], many=True)