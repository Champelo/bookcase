from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from bookcase import models
from bookcase import db
from datetime import datetime, timedelta
from . import book_bp


@book_bp.route('/')
@login_required
def bookcase():
    book_case = db.session.query(models.Book)
    return render_template('view-bookcase.html', user=current_user, book_case=book_case)

@book_bp.route('/book-profile/<string:isbn>')
@login_required
def book_profile(isbn):
    book = db.session.query(models.Book).filter_by(isbn=isbn).first()
    return render_template('book-profile.html', user=current_user, book=book)

@book_bp.route('/add-book', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        isbn = request.form['isbn']
        price = request.form['price']
        if len(isbn) != 13:
            flash('ISBN is not 13 characters')
        elif len(title) < 1:
            flash('Please enter book title')
        elif bool(db.session.query(models.Book.isbn).filter_by(isbn=isbn).first()) == True:
            flash('Book already exists', category='error')
        else:
            new_book = models.Book(title=title, isbn=isbn, bookprice=price)
            db.session.add(new_book)
            db.session.commit()
            return redirect(url_for('book_bp.bookcase'))
    return render_template('addbook.html', user=current_user)

@book_bp.route('/update-book/<string:isbn>', methods=['GET', 'POST'])
@login_required
def update_book(isbn):
    book = db.session.query(models.Book).filter_by(isbn=isbn).first()
    if request.method == 'POST':
        title = request.form['title']
        book.title = title
        db.session.commit()
        return redirect(url_for('book_bp.book_profile', isbn=isbn))
    
    return render_template('update-book.html', user=current_user, book=book)

@book_bp.route('/delete-book/<string:isbn>', methods=['GET', 'POST'])
@login_required
def delete_book(isbn):
    book = db.session.query(models.Book).filter_by(isbn=isbn).first()
    db.session.delete(book)
    db.session.commit()
    flash('Book is successfully deleted', category='success')
    return redirect(url_for('book_bp.bookcase'))

@book_bp.route('/change-status/<string:isbn>/borrower/<int:borrowerID>', methods=['GET'])
@login_required
def choose_borrower(isbn, borrowerID=None):
    book = db.session.query(models.Book).filter_by(isbn=isbn).first()
    book.borrower_id = borrowerID
    book.due_date = datetime.utcnow() + timedelta(days=30)
    book.status = False
    db.session.commit()
    flash('Book is now checked out', category='success')
    return redirect(url_for('book_bp.book_profile', isbn=isbn))

@book_bp.route('/change-status/<string:isbn>', methods=['GET'])
@login_required
def returnBook(isbn):
    book = db.session.query(models.Book).filter_by(isbn=isbn).first()
    book.borrower_id = None
    book.due_date = None
    book.status = True
    db.session.commit()
    flash('Book is now checked-in', category='success')
    return redirect(url_for('book_bp.book_profile', isbn=isbn))