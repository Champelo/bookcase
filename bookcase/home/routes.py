from flask import render_template
from flask_login import login_required, current_user
from . import home_bp
from bookcase import db
from bookcase.models import Book, Borrower
from datetime import datetime

@home_bp.route('/')
@login_required
def dashboard():
    duesoon = db.session.query(Book.title, Book.due_date, Book.isbn, Borrower.fname, Borrower.lname).\
        join(Borrower, Book.borrower_id == Borrower.borrowerId).\
            filter(Book.overdue == False, Book.due_date >= datetime.now()).order_by(Book.due_date).all()

    overdue = db.session.query(Book.title, Book.isbn, Borrower.fname, Borrower.lname).\
        join(Borrower, Book.borrower_id == Borrower.borrowerId).\
            filter(Book.overdue == True).all()
    db.session.close()
    return render_template('dashboard.html', user=current_user, overdue=overdue, duesoon = duesoon)