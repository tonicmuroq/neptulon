# coding: utf-8

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, g, redirect, render_template, url_for, flash

from neptulon.ext import oauth
from neptulon.models import Grant, Token, Client
from neptulon.utils import need_login, need_admin

bp = Blueprint('oauth', __name__, url_prefix='/oauth')
_THOUSAND_DAY = 86400 * 1000


@oauth.clientgetter
def load_client(client_id):
    return Client.get_by_client_id(client_id)


@oauth.grantgetter
def load_grant(client_id, code):
    return Grant.get_by_code_and_client(code, client_id)


@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):
    expires = datetime.now() + timedelta(seconds=_THOUSAND_DAY)
    return Grant.create(g.user.id, client_id, code['code'],
            request.redirect_uri, request.scopes, expires=expires)


@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
    if access_token:
        return Token.get_by_access(access_token)
    return Token.get_by_refresh(refresh_token)


@oauth.tokensetter
def save_token(token, request, *args, **kwargs):
    Token.delete_by_client_and_user(request.client.client_id, request.user.id)
    expires = datetime.now() + timedelta(seconds=_THOUSAND_DAY)

    return Token.create(request.client.client_id, request.user.id, token['token_type'],
            token['access_token'], token['refresh_token'], expires, token['scope'])


@bp.route('/token', methods=['GET', 'POST'])
@oauth.token_handler
def access_token():
    return None


@bp.route('/revoke', methods=['POST'])
@oauth.revoke_handler
def revoke_token():
    pass


@bp.route('/authorize', methods=['GET', 'POST'])
@oauth.authorize_handler
@need_login
def authorize(*args, **kwargs):
    if request.method == 'GET':
        client_id = kwargs.get('client_id')
        client = Client.get_by_client_id(client_id)
        kwargs['client'] = client
        kwargs['user'] = g.user
        return render_template('authorize.html', **kwargs)

    return request.form.get('agree', type=bool, default=False)


@bp.route('/delete_token', methods=['POST'])
@need_login
def delete_token():
    token_id = request.form['token']
    token = Token.get(token_id)
    if not token:
        return jsonify({'message': 'not found'}), 404
    if token.user_id != g.user.id:
        return jsonify({'message': 'not allowed'}), 403
    token.delete()
    return jsonify({'message': 'ok'})


@bp.route('/client', methods=['GET', 'POST'])
@need_admin
def client():
    if request.method == 'GET':
        clients = Client.get_all(g.start, g.limit)
        return render_template('client.html', clients=clients)

    redirect_uri = request.form.get('redirect_uri', default='')
    name = request.form.get('name', default='')
    if not (redirect_uri and name):
        flash(u'缺少需要填写的', 'error')
        return redirect(url_for('oauth.client'))

    Client.create(name, [redirect_uri], ['email'])
    return redirect(url_for('oauth.client'))


@bp.route('/delete_client', methods=['POST'])
@need_admin
def delete_client():
    client_id = request.form['client']
    client = Client.get(client_id)
    client.delete()
    return jsonify({'message': 'ok'})


@bp.route('/authorized', methods=['GET'])
@need_login
def authorized_tokens():
    tokens = Token.get_by_user(g.user.id, g.start, g.limit)
    return render_template('authorized.html', tokens=tokens)


@bp.route('/api/me')
@oauth.require_oauth()
def me():
    user = request.oauth.user
    return jsonify(name=user.name,
            email=user.email,
            real_name=user.real_name,
            token=user.token)
