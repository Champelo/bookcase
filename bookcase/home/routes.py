from flask import render_template
from flask_login import login_required, current_user
from . import home_bp


@home_bp.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)