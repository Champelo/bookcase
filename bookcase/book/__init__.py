from flask import Blueprint

book_bp = Blueprint('book_bp', __name__, template_folder='src', url_prefix='/bookcase')

from . import routes