from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import current_user, login_required
from datetime import datetime, timedelta
import requests
from bookcase import db
from . import book_bp
from bookcase.models import Book, BookSchema, Author, Borrower, booksauthors
from bookcase.forms.fields import DueDateForm
from config import consumer_key



@book_bp.route('/')
@login_required
def bookcase():
    # bookcase = db.session.query(Book.title, Book.isbn, Author.name).all()
    # book_schema = BookSchema(many=True)
    bookcase = db.session.query(Book.title, Book.isbn, Book.thumbnail, Author.name).\
    join(booksauthors, booksauthors.c.book_isbn == Book.isbn).\
        join(Author, booksauthors.c.author_id == Author.id)

    book_schema = BookSchema(many=True)
    return render_template('view-bookcase.html', user=current_user, bookcase=bookcase)

@book_bp.route('/book-profile/<string:isbn>')
@login_required
def book_profile(isbn):
    book = db.session.query(Book.title, Book.isbn, Book.status,
    Book.overdue, Book.thumbnail, Author.name).\
        filter_by(isbn=isbn).\
        join(booksauthors, booksauthors.c.book_isbn == Book.isbn).\
            join(Author, booksauthors.c.author_id == Author.id).\
                first()
    #Query to run if the book is checkout since it will have a borrower.
    if not book.status:
        book = db.session.query(Book.title, Book.isbn, Book.status,
        Book.overdue, Book.due_date, Book.thumbnail, Borrower.fname, Borrower.lname, Author.name).\
            filter_by(isbn=isbn).\
            join(booksauthors, booksauthors.c.book_isbn == Book.isbn).\
                join(Author, booksauthors.c.author_id == Author.id).\
                    join(Borrower, Book.borrower_id == Borrower.borrowerId).\
                        first()
    
    return render_template('book-profile.html', user=current_user, book=book)

@book_bp.route('/browse-books', methods=['GET', 'POST'])
@login_required
def browse_books():
    books = []
    next_page = False
    if 'gbook_q' in session:
        q = session['gbook_q']
        next_page = True
    if request.method == 'POST' or next_page:
        if 'gbook_q' not in session:
            q = request.form['q']
            session['gbook_q'] = q
        elif request.method == 'POST' and q:
            session.pop('gbook_q')
        page = request.args.get('page', 1, type=int)
        response = requests.get('https://www.googleapis.com/books/v1/volumes?q=' + q + 
        '&orderBy=relevance&startIndex=' + str(page) + '&key=' + consumer_key)
        if response.status_code != 200:
            print('Error')
        data = response.json()
        books = data['items']
        next_page = False
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
    if "imageLinks" in book:
        thumbnail = book['imageLinks']['thumbnail']
    else:
        thumbnail = None
    price = None
    new_book = Book(title=title, isbn=isbn, bookprice=price, thumbnail=thumbnail)
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
    
@book_bp.route('/update-duedate/<string:isbn>', methods=['GET', 'POST'])
@login_required
def update_duedate(isbn):
    book = db.session.query(Book).filter_by(isbn=isbn).first()
    form = DueDateForm()
    if form.validate_on_submit():
        # date = datetime.strptime(due_date, '%Y-%m-%d').date()
        book.due_date = form.date.data
        if form.date.data >= datetime.now().date():
            book.overdue = False
        db.session.commit()
        return redirect(url_for('book_bp.book_profile', isbn=isbn))
    
    return render_template('update-duedate.html', user=current_user, book=book, form=form)

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
