# coding: utf-8

from flask import Blueprint, request, jsonify

from neptulon.models import Auth


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
