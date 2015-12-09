# coding: utf-8

from flask import Blueprint, request, jsonify

from neptulon.models import Auth, User


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/profile', methods=['GET'])
def get_profile():
    token = request.values.get('token', '')
    if not token:
        token = request.headers.get('X-Neptulon-Token', '')

    auth = Auth.get_by_token(token)
    if not auth:
        return jsonify({}), 404

    return jsonify(auth.user.to_dict()), 200


@bp.route('/check', methods=['POST'])
def check_user():
    name = request.form.get('name', '')
    password = request.form.get('password', '')

    user = User.get_by_name(name) or User.get_by_email(name)
    if not (user and user.check_password(password)):
        return jsonify({'message': 'no'}), 403
    return jsonify({'message': 'yes'}), 200
