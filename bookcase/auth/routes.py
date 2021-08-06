from flask import render_template, request, redirect, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
from bookcase.forms.fields import LoginForm, SignupForm
from bookcase.models import User 
from bookcase import db


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(email=form.email.data).first()
        login_user(user)
        return redirect(url_for('home_bp.dashboard'))
    return render_template('login.html', user=current_user, form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', category='success')
    return redirect(url_for('auth_bp.login'))

@auth_bp.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = SignupForm()
    if form.validate_on_submit():
        new_user = User(email=form.email.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home_bp.dashboard'))
    return render_template('signup.html', form=form)