from flask import render_template, request, redirect, flash, url_for
from bookcase import db
from bookcase import models
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if bool(db.session.query(models.User.email).filter_by(email=email).first()) == False:
            flash("Email doesn't exist", category='error')
        elif bool(db.session.query(models.User.password).filter_by(password=password).first()) == False:
            flash("Incorrect password", category='error')
        else:
            user = db.session.query(models.User).filter_by(email=email).first()
            login_user(user)
            return redirect(url_for('home_bp.dashboard'))
    
    return render_template('login.html', user=current_user)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', category='success')
    return redirect(url_for('auth_bp.login'))

@auth_bp.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        con_password = request.form['con_password']
        if len(email) < 4:
            flash("Email shorter than 4", category='error')
        elif len(password) < 4:
            flash("Password shorter than 8", category='error')
        elif password != con_password:
            flash("Passwords don't match", category='error')
        elif bool(db.session.query(models.User.email).filter_by(email=email).first()) == True:
            flash('Email already exists', category='error')
        else:
            new_user = models.User(email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home_bp.dashboard'))
    return render_template('sign-up.html')