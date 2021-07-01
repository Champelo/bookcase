from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from bookcase.models import Book, Author, Borrower
from bookcase import db
from datetime import datetime, timedelta
from . import book_bp
from decimal import Decimal
from config import consumer_key
import requests



@book_bp.route('/')
@login_required
def bookcase():
    book_case = db.session.query(Book)
    return render_template('view-bookcase.html', user=current_user, book_case=book_case)

@book_bp.route('/book-profile/<string:isbn>')
@login_required
def book_profile(isbn):
    book = db.session.query(Book).filter_by(isbn=isbn).first()
    authors = book.authors
    return render_template('book-profile.html', user=current_user, book=book, authors=authors)

@book_bp.route('/browse-books')
@login_required
def browse_books():
    response = requests.get('https://www.googleapis.com/books/v1/volumes?q=The Cat in the Hat&orderBy=relevance&key=' + consumer_key)
    if response.status_code != 200:
        print('Error')
    data = response.json()
    books = data['items']
    return render_template('browse-books.html', user=current_user, books=books)

@book_bp.route('/gbook-profile', methods=['GET', 'POST'])
@login_required
def gbook_profile():
    link = request.args.get('link')
    response = requests.get(link)
    if response.status_code != 200:
        print('Error')
    data = response.json()
    return render_template('gbook-profile.html', user=current_user, data=data)

@book_bp.route('/add-book', methods=['GET', 'POST'])
@login_required
def add_book():
    link = request.args.get('link')
    response = requests.get(link)
    if response.status_code != 200:
        print('Error')
    data = response.json()
    book = data['volumeInfo']
    title = book['title']
    for isbn in book['industryIdentifiers']:
        if isbn['type'] == 'ISBN_13':
            isbn = isbn['identifier']
    authors = book['authors']
    price = None
    new_book = Book(title=title, isbn=isbn, bookprice=price)
    db.session.add(new_book)
    db.session.commit()
    for author in authors:
        new_author = Author(name=author)
        author_exist = db.session.query(Author).filter_by(name=author).first()
        db.session.commit()
        if not author_exist:
            db.session.add(new_author)
            new_book.authors.append(new_author)
        else:
            new_book.authors.append(author_exist)
    db.session.commit()
    return redirect('http://127.0.0.1:5000/bookcase/gbook-profile?link=' +  data['selfLink'])
    
@book_bp.route('/update-book/<string:isbn>', methods=['GET', 'POST'])
@login_required
def update_book(isbn):
    book = db.session.query(Book).filter_by(isbn=isbn).first()
    if request.method == 'POST':
        bookprice = request.form['bookprice']
        if book.bookprice < Decimal(bookprice):
            pricediff = Decimal(bookprice) - book.bookprice
            current_user.bud_remaining = current_user.bud_remaining - pricediff
        elif book.bookprice > Decimal(bookprice):
            pricediff = book.bookprice - Decimal(bookprice)
            current_user.bud_remaining = current_user.bud_remaining + pricediff
        book.bookprice = bookprice
        if book.due_date is not None:
            due_date = request.form['due_date']
            date = datetime.strptime(due_date, '%Y-%m-%d').date()

            if date < datetime.now().date() and date != book.due_date:
                flash("Date has to after today", category='error')
            else:
                book.due_date = date
                if date >= datetime.now().date():
                    book.overdue = False
        db.session.commit()
        return redirect(url_for('book_bp.book_profile', isbn=isbn))
    
    return render_template('update-book.html', user=current_user, book=book)

@book_bp.route('/delete-book/<string:isbn>', methods=['GET', 'POST'])
@login_required
def delete_book(isbn):
    book = db.session.query(Book).filter_by(isbn=isbn).first()
    authors = book.authors
    for author in authors:
        if len(author.books) <= 1:
            db.session.delete(author)
    current_user.bud_remaining = current_user.bud_remaining + book.bookprice
    db.session.delete(book)
    db.session.commit()
    flash('Book is successfully deleted', category='success')
    return redirect(url_for('book_bp.bookcase'))

@book_bp.route('/change-status/<string:isbn>/borrower/<int:borrowerID>', methods=['GET'])
@login_required
def choose_borrower(isbn, borrowerID=None):
    book = db.session.query(Book).filter_by(isbn=isbn).first()
    book.borrower_id = borrowerID
    book.due_date = datetime.utcnow() + timedelta(days=30)
    book.status = False
    db.session.commit()
    flash('Book is now checked out', category='success')
    return redirect(url_for('book_bp.book_profile', isbn=isbn))

@book_bp.route('/change-status/<string:isbn>', methods=['GET'])
@login_required
def returnBook(isbn):
    book = db.session.query(Book).filter_by(isbn=isbn).first()
    borrower = db.session.query(Borrower).filter_by(borrowerId=book.borrower_id).first()
    if book.overdue:
        borrower.rating -= 0.5
    elif borrower.rating < 5:
        borrower.rating += 0.5
    book.borrower_id = None
    book.due_date = None
    book.status = True
    db.session.commit()
    flash('Book is now checked-in', category='success')
    return redirect(url_for('book_bp.book_profile', isbn=isbn))
