from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from bookcase.models import Borrower, Book
from bookcase import db
from . import borrower_bp
from bookcase.forms.fields import BorrowerForm

@borrower_bp.route('/')
@login_required
def view_borrowers():
    borrowers = db.session.query(Borrower).order_by(Borrower.fname)
    return render_template('view-borrowers.html', user=current_user, borrowers=borrowers)

@borrower_bp.route('/<int:borrowerID>')
@login_required
def borrower_profile(borrowerID):
    borrower = db.session.query(Borrower).filter_by(borrowerId=borrowerID).first()
    return render_template('borrower-profile.html', user=current_user, borrower=borrower)

@borrower_bp.route('/add-new', methods=['GET', 'POST'])
@login_required
def add_borrower():
    form = BorrowerForm()
    if form.validate_on_submit():
        new_borrower = Borrower(fname=form.fname.data, lname=form.lname.data)
        db.session.add(new_borrower)
        db.session.commit()
        return redirect(url_for('borrower_bp.view_borrowers'))
    return render_template('addnewborrower.html', user=current_user, form=form)

@borrower_bp.route('/<int:borrowerID>/update-borrower', methods=['GET', 'POST'])
@login_required
def update_borrower(borrowerID):
    form = BorrowerForm() 
    borrower = db.session.query(Borrower).filter_by(borrowerId=borrowerID).first()
    if form.validate_on_submit():
        borrower.fname = form.fname.data
        borrower.lname = form.lname.data
        db.session.commit()
        return redirect(url_for('borrower_bp.borrower_profile', borrowerID=borrowerID))
    
    return render_template('update-borrower.html', user=current_user, borrower=borrower, form=form)

@borrower_bp.route('/<int:borrowerID>/delete', methods=['GET', 'POST'])
@login_required
def delete_borrower(borrowerID):
    borrower = db.session.query(Borrower).filter_by(borrowerId=borrowerID).first()
    db.session.delete(borrower)
    db.session.commit()
    flash('Borrower is successfully deleted', category='success')
    return redirect(url_for('borrower_bp.view_borrowers'))

@borrower_bp.route('/change-status/<string:isbn>/choose-borrower', methods=['GET'])
@login_required
def view_choose_borrower(isbn):
    borrowers = db.session.query(Borrower)
    book = db.session.query(Book).filter_by(isbn=isbn).first()
    return render_template('checkout.html', user=current_user, borrowers=borrowers, book=book)