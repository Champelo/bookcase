from flask import Blueprint

budget_bp = Blueprint('budget_bp', __name__, template_folder='src', url_prefix='/user/budget')

from . import routes