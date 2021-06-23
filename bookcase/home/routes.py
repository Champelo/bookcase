from flask import render_template
from flask_login import login_required, current_user
from . import home_bp
from bookcase import models, db
from datetime import datetime

@home_bp.route('/')
@login_required
def dashboard():
    books = db.session.query(models.Book.title, models.Book.due_date, 
    models.Borrower.fname, models.Borrower.lname, models.Borrower.borrowerId).\
        join(models.Borrower, models.Book.borrower_id == models.Borrower.borrowerId).\
            filter(models.Book.overdue == True).all()
    return render_template('dashboard.html', user=current_user, books=books)