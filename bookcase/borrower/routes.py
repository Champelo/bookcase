from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from bookcase import models
from bookcase import db
from . import borrower_bp

@borrower_bp.route('/')
@login_required
def view_borrowers():
    borrowers = db.session.query(models.Borrower)
    db.session.close()
    return render_template('view-borrowers.html', user=current_user, borrowers=borrowers)

@borrower_bp.route('/<int:borrowerID>')
@login_required
def borrower_profile(borrowerID):
    borrower = db.session.query(models.Borrower).filter_by(borrowerId=borrowerID).first()
    db.session.close()
    return render_template('borrower-profile.html', user=current_user, borrower=borrower)

@borrower_bp.route('/add-new', methods=['GET', 'POST'])
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
                new_borrower = models.Borrower(fname=fname, lname=lname)
                db.session.add(new_borrower)
                db.session.commit()
                db.session.close()
                return redirect(url_for('borrower_bp.view_borrowers'))
    return render_template('addborrower.html', user=current_user)

@borrower_bp.route('/<int:borrowerID>/update-borrower', methods=['GET', 'POST'])
@login_required
def update_borrower(borrowerID):
    borrower = db.session.query(models.Borrower).filter_by(borrowerId=borrowerID).first()
    db.session.close()
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        borrower.fname = fname
        borrower.lname = lname
        db.session.commit()
        db.session.close()
        return redirect(url_for('borrower_bp.borrower_profile', borrowerID=borrowerID))
    
    return render_template('update-borrower.html', user=current_user, borrower=borrower)

@borrower_bp.route('/<int:borrowerID>/delete', methods=['GET', 'POST'])
@login_required
def delete_borrower(borrowerID):
    borrower = db.session.query(models.Borrower).filter_by(borrowerId=borrowerID).first()
    db.session.delete(borrower)
    db.session.commit()
    db.session.close()
    db.session.close()
    flash('Borrower is successfully deleted', category='success')
    return redirect(url_for('borrower_bp.view_borrowers'))

@borrower_bp.route('/change-status/<string:isbn>/choose-borrower', methods=['GET'])
@login_required
def view_choose_borrower(isbn):
    borrowers = db.session.query(models.Borrower)
    book = db.session.query(models.Book).filter_by(isbn=isbn).first()
    db.session.close()
    return render_template('checkout.html', user=current_user, borrowers=borrowers, book=book)