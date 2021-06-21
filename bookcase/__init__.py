from os import path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os.path
from flask_login import LoginManager
from .schedules import overdue_check

db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        #FIXME: Remember to change this to something more secure when deploying.
        SECRET_KEY='123'
    )
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookcase.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    db.app = app
    db.init_app(app) 
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth_bp.login'
    login_manager.login_message = 'Please login'

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    try:
        os.mkdir(app.instance_path)
    except OSError:
        pass
    

    from .models import User

    if path.exists('bookcase/bookcase.db') == False:
        with app.app_context():
            db.create_all()

    from .auth import auth_bp
    from .home import home_bp
    from .book import book_bp
    from .borrower import borrower_bp
    from .budget import budget_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(borrower_bp)
    app.register_blueprint(budget_bp)
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(id)

    return app



