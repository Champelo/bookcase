from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from bookcase import models
from bookcase import db
from . import budget_bp
from decimal import Decimal

@budget_bp.route('/')
@login_required
def budget_home():
    return render_template('budget-home.html', user=current_user)

@budget_bp.route('/change-budget', methods=['GET', 'POST'])
@login_required
def change_budget():
    if request.method == 'POST':
        budget = request.form['budget']
        newbudprice = current_user.budget - current_user.bud_remaining
        current_user.budget = budget
        current_user.bud_remaining = Decimal(budget) - newbudprice
        db.session.commit()
        return redirect(url_for('budget_bp.budget_home'))

    return render_template('change-budget.html', user=current_user)

@budget_bp.route('/delete-budget', methods=['GET'])
@login_required
def delete_budget():
    current_user.budget = 0.00
    current_user.bud_remaining = 0.00
    db.session.commit()
    return redirect(url_for('budget_bp.budget_home'))


@budget_bp.route('/spending-log')
@login_required
def spending_log():
    books = db.session.query(models.Book)
    return render_template('spending-log.html', user=current_user, books=books)

@budget_bp.route('/decrease-remaining/<string:isbn>')
@login_required
def decrease_remaining(isbn):
    book = db.session.query(models.Book).filter_by(isbn=isbn).first()
    current_user.bud_remaining = current_user.bud_remaining - book.bookprice
    db.session.commit()
    return redirect(url_for('book_bp.bookcase'))


