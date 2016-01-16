# coding: utf-8

from flask import Blueprint, request, g, redirect, url_for, session, render_template, flash, jsonify, make_response, render_template_string
from flask.ext.mail import Message

from neptulon.ext import mail
from neptulon.config import MAIL_USERNAME, rdb
from neptulon.models import Auth, User, Pubkey
from neptulon.utils import need_login, login_user, gen_fingerprint, list_keys_by_userid, get_key_by_userid, delete_key_by_userid, add_key, get_key

import sys

reload(sys)
sys.setdefaultencoding('utf8')

bp = Blueprint('ui', __name__, url_prefix='/ui')


@bp.route('/', methods=['GET'])
@need_login
def index():
    auths = g.user.get_auths()
    name  = session['name']
    user = User.get_by_name(name)
    return render_template('/auths.html', auths=auths, user=user)


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

@bp.route('/refresh_token', methods=['POST'])
@need_login
def refresh_token():
    user_id = request.form['user_id']
    user = User.get(user_id)
    
    pubkeys = list_keys_by_userid(user_id)
    print(pubkeys)
    for key in pubkeys:
        delete_key_by_userid(user_id, key['fingerprint'])
    token = user.refresh_token()
    return jsonify({'message': user.token}), 200


@bp.route('/download_config', methods=['GET'])
@need_login
def download_config():
    #user_id = request.form['user_id']
    user = User.get(session['id'])
    resp = make_response()
    resp.headers['Content-Type'] = "application/octet-stream"
    resp.headers['Pragma'] = "No-cache"
    resp.headers['Cache-Control'] = "No-cache"
    resp.headers['Content-Disposition'] = "attachment; filename='ricebook-mobile.config'"
    f = open('./ricebook-template.mobileconfig', 'rb')
    try:
        temp = f.read()
    finally:
        f.close()

    temp = render_template_string(temp, username=user.name, password=user.token)
    resp.data = temp
    return resp

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

@bp.route('/pubkey', methods=['GET'])
@need_login
def pubkeys():
    pubkeys = list_keys_by_userid(session['id'])
    return render_template('/pubkeys.html', pubkeys=pubkeys)


@bp.route('/add_pubkey', methods=['GET', 'POST'])
@need_login
def add_pubkey():
    if request.method == 'GET':
        return render_template('/add_pubkey.html')

    title = request.form['title']
    pkey = request.form['pkey']

    ret = get_key(session['id'], pkey, title)
    if ret:
        flash(u'重复啦', 'error')
        return render_template('/add_pubkey.html')

    ret = add_key(session['id'], pkey, title)
    return redirect(url_for('ui.pubkeys'))

@bp.route('/delete_pubkey', methods=['POST'])
@need_login
def delete_pubkey():
    keyfp = request.form['keyfp']
    pubkey = get_key_by_userid(session['id'], keyfp)
    if pubkey:
        delete_key_by_userid(session['id'], keyfp)
    else:
        return jsonify({'message': 'pub key does not exist'}), 200
    return jsonify({'message': 'ok'}), 200


@bp.route('/forget_password', methods=['POST', 'GET'])
def forget_password():
    if request.method == 'GET':
        return render_template('/forget_password.html', email='')

    email = request.form['email']
    user = User.get_by_email(email)
    if not user:
        flash(u'没这个人啊', 'error')
        return render_template('/forget_password.html', email='')

    message = Message(
                subject=u'重置内网 OPENID 密码',
                sender=MAIL_USERNAME,
                recipients=[email]
            )
    message.html = render_template('/email/reset_password.html', user=user)
    mail.send(message)
    return render_template('/forget_password.html', email=email)


@bp.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_password(token):
    user = User.get_by_token(token)
    if not user:
        flash(u'没有这个人啊', 'error')
        return render_template('/reset_password.html', token=token)

    if request.method == 'GET':
        return render_template('/reset_password.html', token=token)

    password = request.form['password']
    confirm_password = request.form['confirm_password']
    if password != confirm_password:
        flash(u'两次输入不对, 你是鱼么这么快就忘记了', 'error')
        return render_template('/reset_password.html', token=token)

    user.set_password(password)
    user.refresh_token()
    login_user(user)
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
