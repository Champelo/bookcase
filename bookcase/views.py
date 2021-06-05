from flask import render_template, Blueprint, request, redirect, url_for, flash
from flask_login import current_user, login_required
from .models import Book
from . import db

views_blueprint = Blueprint('views', __name__, url_prefix='/user')

@views_blueprint.route('/dashboard')
@login_required
def dashboard():
    return render_template('bookcase-app/dashboard.html', user=current_user)

@views_blueprint.route('/view-bookcase')
@login_required
def view_bookcase():
    book_case = db.session.query(Book)
    return render_template('bookcase-app/view-bookcase.html', user=current_user, book_case=book_case)

@views_blueprint.route('/add-book', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        isbn = request.form['isbn']
        if len(isbn) != 13:
            flash('ISBN is not 13 characters')
        elif len(title) < 1:
            flash('Please enter book title')
        elif bool(db.session.query(Book.isbn).filter_by(isbn=isbn).first()) == True:
            flash('Book already exists', category='error')
        else:
            new_book = Book(title=title, isbn=isbn)
            db.session.add(new_book)
            db.session.commit()
            return redirect(url_for('views.view_bookcase'))
    return render_template('bookcase-app/addbook.html', user=current_user)

@views_blueprint.route('/book-profile/<string:isbn>')
@login_required
def book_profile(isbn):
    book = db.session.query(Book).filter_by(isbn=isbn).first()
    return render_template('bookcase-app/book-profile.html', user=current_user, book=book)

@views_blueprint.route('/update-book/<string:isbn>', methods=['GET', 'POST'])
@login_required
def update_book(isbn):
    book = db.session.query(Book).filter_by(isbn=isbn).first()
    if request.method == 'POST':
        title = request.form['title']
        book.title = title
        db.session.commit()
        return redirect(url_for('views.book_profile', isbn=isbn))
    
    return render_template('bookcase-app/update.html', user=current_user, book=book)