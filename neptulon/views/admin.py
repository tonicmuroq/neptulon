# coding:utf-8

import sys
from flask import Blueprint, request, redirect, url_for, render_template, flash, jsonify, abort, g
from neptulon.utils import need_admin
from neptulon.models import User, RSAKey

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/', methods=['GET'])
def index():
    admin = request.args.get('admin')
    users, total = User.list_users(admin=admin, start=g.start, limit=g.limit)
    return render_template('/admin.html', users=users,
            total=total, endpoint='admin.index', admin=admin)


@bp.route('/edit/<int:uid>', methods=['GET', 'POST'])
def edit(uid):
    u = User.get(uid)
    if not u:
        abort(403)

    if request.method == 'GET':
        return render_template('/admin_edit.html', user=u)

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    real_name = request.form['real_name']

    if not (name and email and real_name):
        flash(u'你有些忘记填了', 'error')
        return render_template('/admin_edit.html', user=u.id)

    u.edit(name, email, password, real_name)
    return redirect(url_for('admin.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('/register.html')

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    real_name = request.form['real_name']
    if not (name and email and password and real_name):
        flash(u'你有些忘记填了', 'error')
        return render_template('/register.html')

    u = User.create(name, email, password, real_name)
    if not u:
        flash(u'已经存在, 登录去吧', 'error')
        return render_template('/register.html')

    if not u.send_doc_email():
        flash(u'不好，发送邮件失败', 'error')
        return render_template('/register.html')
    return redirect(url_for('admin.index'))


@bp.route('/delete_user', methods=['POST'])
def delete_user():
    user_id = request.form['user_id']
    user = User.get(user_id)
    if not user:
        return jsonify({'message': 'not found'}), 404

    pubkey = RSAKey.get_by_user_id(user_id)
    if pubkey:
        pubkey.delete()
    user.delete()

    return jsonify({'message': 'ok'}), 200


@bp.route('/sudo', methods=['POST'])
def sudo():
    user_id = request.form['user_id']
    user = User.get(user_id)
    if not user:
        return jsonify({'message': 'not found'}), 404

    user.sudo()
    return jsonify({'message': 'ok'}), 200


@bp.before_request
@need_admin
def access_control():
    pass
