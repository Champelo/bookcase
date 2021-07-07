from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, ValidationError, Email, EqualTo
from bookcase import models, db


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

    def validate_email(self, email):
        user = db.session.query(models.User.email).filter_by(email=email.data).first()
        if not user:
            raise ValidationError('Email does not exist. Please try again.')
    
    def validate_password(self, password):
        user = db.session.query(models.User.password).filter_by(password=password.data).first()
        if not user:
            raise ValidationError('Incorrect password. Please try again.')

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), 
        Length(min=5, max=20, message='Please enter a password that is greater than 5')])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password', message='Passwords do not match.')])

    def validate_email(self, email):
        user = db.session.query(models.User.email).filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already used on a account. Please try another email or click forgot password.')