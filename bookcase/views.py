from flask import render_template, Blueprint
from flask_login import current_user, login_required


views_blueprint = Blueprint('views', __name__, url_prefix='/user')

@views_blueprint.route('/dashboard')
@login_required
def dashboard():
    return render_template('bookcase-app/dashboard.html', user=current_user)




