from flask import Blueprint

auth_bp = Blueprint('auth_bp', __name__,  template_folder='src', url_prefix='/auth')

from . import routes