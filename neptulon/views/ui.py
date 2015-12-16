# coding: utf-8

from flask import Blueprint, request, g, redirect, url_for, session, render_template, flash, jsonify

from neptulon.models import Auth, User
from neptulon.utils import need_login, login_user


bp = Blueprint('ui', __name__, url_prefix='/ui')


@bp.route('/', methods=['GET'])
@need_login
def index():
    auths = g.user.get_auths()
    return render_template('/auths.html', auths=auths)


@bp.route('/delete_auth', methods=['POST'])
@need_login
def delete_auth():
    auth_id = request.form['auth_id']
    auth = Auth.get(auth_id)
    if not auth:
        return jsonify({'message': 'not found'}), 404
    if not auth.user_id == g.user.id:
        return jsonify({'message': 'not allowed'}), 403
    auth.delete()
    return jsonify({'message': 'ok'}), 200


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if not g.user:
            return render_template('/login.html')
        return redirect(url_for('ui.index'))

    name = request.form['name']
    password = request.form['password']
    if not (name and password):
        flash(u'你有些忘记填了', 'error')
        return render_template('/login.html')

    u = User.get_by_name(name) or User.get_by_email(name)
    if not (u and u.check_password(password)):
        flash(u'密码错了, 或者你就不存在啊', 'error')
        return render_template('/login.html')

    login_user(u)

    redir = request.values.get('redirect', url_for('ui.index'))
    return redirect(redir)


@bp.route('/password', methods=['GET', 'POST'])
@need_login
def password():
    if request.method == 'GET':
        return render_template('/password.html')

    password = request.form['password']
    confirm_password = request.form['confirm_password']
    if password != confirm_password:
        flash(u'两次输入不对, 你是鱼么这么快就忘记了', 'error')
        return render_template('/password.html')

    g.user.set_password(password)
    return redirect(url_for('ui.index'))


@bp.route('/logout', methods=['GET', 'POST'])
@need_login
def logout():
    session.pop('id', None)
    return redirect(url_for('ui.login'))


@bp.route('/authenticate', methods=['GET', 'POST'])
@need_login
def authenticate():
    url = request.values['url']
    redir = request.values['redirect']
    if request.method == 'GET':
        auth = Auth.get_by_user_and_url(g.user.id, url)
        if auth:
            redir = '%s?token=%s' % (redir, auth.token)
            return redirect(redir)

        return render_template('/authenticate.html', url=url, redir=redir)

    if request.form.get('agree', ''):
        auth = Auth.get_or_create(g.user.id, url)
        if auth:
            redir = '%s?token=%s' % (redir, auth.token)
    return redirect(redir)
