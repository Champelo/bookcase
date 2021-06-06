from flask import render_template, Blueprint, request, redirect, url_for, flash
from flask_login import current_user, login_required
from .models import Book, Borrower
from . import db
from datetime import datetime, timedelta

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
        price = request.form['price']
        if len(isbn) != 13:
            flash('ISBN is not 13 characters')
        elif len(title) < 1:
            flash('Please enter book title')
        elif bool(db.session.query(Book.isbn).filter_by(isbn=isbn).first()) == True:
            flash('Book already exists', category='error')
        else:
            new_book = Book(title=title, isbn=isbn, bookprice=price)
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
    
    return render_template('bookcase-app/update-book.html', user=current_user, book=book)

@views_blueprint.route('/delete-book/<string:isbn>', methods=['GET', 'POST'])
@login_required
def delete_book(isbn):
    book = db.session.query(Book).filter_by(isbn=isbn).first()
    db.session.delete(book)
    db.session.commit()
    flash('Book is successfully deleted', category='success')
    return redirect(url_for('views.view_bookcase'))

@views_blueprint.route('/change-status/<string:isbn>', methods=['GET', 'POST'])
@login_required
def change_status(isbn):
    book = db.session.query(Book).filter_by(isbn=isbn).first()
    book.book_status = not book.book_status
    if not book.book_status:
        book.due_date = datetime.utcnow() + timedelta(days=30)
    else:
        book.due_date = None
    db.session.commit()
    return redirect(url_for('views.book_profile', isbn=isbn))

@views_blueprint.route('/borrowers/add-new', methods=['GET', 'POST'])
@login_required
def add_borrower():
    if request.method == 'POST':
            fname = request.form['fname']
            lname = request.form['lname']
            if len(fname) < 1:
                flash('Please enter first name')
            elif len(lname) < 1:
                flash('Please enter last name')
            else:
                new_borrower = Borrower(fname=fname, lname=lname)
                db.session.add(new_borrower)
                db.session.commit()
                return redirect(url_for('views.view_borrowers'))
    return render_template('bookcase-app/addborrower.html', user=current_user)

@views_blueprint.route('/borrowers')
@login_required
def view_borrowers():
    borrowers = db.session.query(Borrower)
    return render_template('bookcase-app/view-borrowers.html', user=current_user, borrowers=borrowers)

@views_blueprint.route('/borrowers/<int:id>')
@login_required
def borrower_profile(id):
    borrower = db.session.query(Borrower).filter_by(id=id).first()
    return render_template('bookcase-app/borrower-profile.html', user=current_user, borrower=borrower)

@views_blueprint.route('/borrowers/<int:id>/update-borrower', methods=['GET', 'POST'])
@login_required
def update_borrower(id):
    borrower = db.session.query(Borrower).filter_by(id=id).first()
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        borrower.fname = fname
        borrower.lname = lname
        db.session.commit()
        return redirect(url_for('views.borrower_profile', id=id))
    
    return render_template('bookcase-app/update-borrower.html', user=current_user, borrower=borrower)

@views_blueprint.route('/borrowers/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete_borrower(id):
    borrower = db.session.query(Borrower).filter_by(id=id).first()
    db.session.delete(borrower)
    db.session.commit()
    flash('Borrower is successfully deleted', category='success')
    return redirect(url_for('views.view_borrowers'))