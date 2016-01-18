# coding: utf-8

from flask import Blueprint, request, render_template
from neptulon.models import User

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/get_token', methods=['POST'])
def get_token():
    name = request.form['name']
    user = User.get_by_name(name)
    if user:
        return user.token, 200
    else:
        return render_template('/400.html'), 400
