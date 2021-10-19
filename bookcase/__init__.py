from os import path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os.path
from flask_login import LoginManager
from config import Config
from flask_migrate import Migrate
from flask_assets import Environment, Bundle
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()


def create_app(test_config=None, config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    migrate = Migrate(app, db)

    assets = Environment(app)
    assets.url = app.static_url_path
    scss = Bundle('asset/scss/main.scss', filters='pyscss', output='main.css')

    
    assets.register('scss', scss)
    db.app = app


    db.init_app(app)
    migrate.init_app(app, db)
    scheduler.init_app(app)
    scheduler.start() 

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


from bookcase.task import scheduler