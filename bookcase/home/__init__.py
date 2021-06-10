from flask import Blueprint

home_bp = Blueprint('home_bp', __name__, template_folder='src', url_prefix='/dashboard')

from . import routes