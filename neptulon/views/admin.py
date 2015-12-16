#!/usr/bin/python
#coding:utf-8

from flask import Blueprint, request, redirect, url_for, render_template, flash, jsonify

from neptulon.utils import need_admin
from neptulon.models import User

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/', methods=['GET'])
@need_admin
def index():
    users, total = User.list_users()
    return render_template('/admin.html', users=users, total=total, endpoint='admin.index')


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

    return redirect(url_for('admin.index'))

@bp.route('/delete_user', methods=['POST'])
@need_admin
def delete_user():
    user_id = request.form['user_id']
    user = User.get(user_id)
    if not user:
        return jsonify({'message': 'not found'}), 404
    user.delete()
    return jsonify({'message': 'ok'}), 200

@bp.route('/sudo', methods=['POST'])
@need_admin
def sudo():
    user_id = request.form['user_id']
    user = User.get(user_id)
    if not user:
        return jsonify({'message': 'not found'}), 404
    user.sudo()
    return jsonify({'message': 'ok'}), 200

