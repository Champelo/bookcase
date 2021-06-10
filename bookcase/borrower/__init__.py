from flask import Blueprint

borrower_bp = Blueprint('borrower_bp', __name__, template_folder='src', url_prefix='/borrowers')

from . import routes