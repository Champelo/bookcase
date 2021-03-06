from flask import render_template, redirect, url_for
from flask_login import current_user, login_required
from bookcase.models import Book
from bookcase import db
from . import budget_bp
from decimal import Decimal
from bookcase.forms.fields import BudgetForm

@budget_bp.route('/')
@login_required
def budget_home():
    books = db.session.query(Book).order_by(Book.purchased_date.desc())
    return render_template('budget-home.html', user=current_user, books=books)

@budget_bp.route('/change-budget', methods=['GET', 'POST'])
@login_required
def change_budget():
    form = BudgetForm()
    if form.validate_on_submit():
        budget = form.bookprice.data
        amount_spent = current_user.budget - current_user.bud_remaining
        current_user.budget = budget
        current_user.bud_remaining = Decimal(budget) - amount_spent
        db.session.commit()
        return redirect(url_for('budget_bp.budget_home'))

    return render_template('change-budget.html', user=current_user, form=form)

@budget_bp.route('/delete-budget', methods=['GET'])
@login_required
def delete_budget():
    current_user.budget = 0.00
    current_user.bud_remaining = 0.00
    db.session.commit()
    return redirect(url_for('budget_bp.budget_home'))

@budget_bp.route('/decrease-remaining/<string:isbn>')
@login_required
def decrease_remaining(isbn):
    book = db.session.query(Book).filter_by(isbn=isbn).first()
    current_user.bud_remaining = current_user.bud_remaining - book.bookprice
    db.session.commit()
    return redirect(url_for('book_bp.bookcase'))

@budget_bp.route('/update-bookprice/<string:isbn>', methods=['GET', 'POST'])
@login_required
def update_bookprice(isbn):
    book = db.session.query(Book).filter_by(isbn=isbn).first()
    form = BudgetForm()
    if form.validate_on_submit():
        new_price = Decimal(form.bookprice.data)
        if book.bookprice < new_price:
            pricediff = new_price - book.bookprice
            current_user.bud_remaining = current_user.bud_remaining - pricediff
        elif book.bookprice > new_price:
            pricediff = book.bookprice - new_price
            current_user.bud_remaining = current_user.bud_remaining + pricediff
        book.bookprice = new_price
        db.session.commit()
        return redirect(url_for('budget_bp.budget_home'))
    
    return render_template('update-bookprice.html', user=current_user, book=book, form=form)

