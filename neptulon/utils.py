# coding:utf-8

from functools import wraps
from flask import g, redirect, url_for, session, request, flash, render_template
from neptulon.models import User
from neptulon.config import rdb
import hashlib
import base64

def need_login(f):
    @wraps(f)
    def _(*args, **kwargs):
        if not g.user:
            return redirect(url_for('ui.login', redirect=request.url))
        return f(*args, **kwargs)
    return _


def need_admin(f):
    @wraps(f)
    def _(*args, **kwargs):
        if not g.user or not g.user.privilege:
            return redirect(url_for('ui.index'))
        return f(*args, **kwargs)
    return _


def login_user(user):
    session['id'] = user.id
    session['name'] = user.name


def paginator_kwargs(kw):
    d = kw.copy()
    d.pop('start', None)
    d.pop('limit', None)
    return d

def gen_fingerprint(line):
    line = line.strip().split()
    key = base64.b64decode(line[len(line)-2].encode('ascii'))
    return hashlib.md5(key).hexdigest().upper()




def list_keys_by_userid(userid):
    user = User.get(userid)
    res_pubkeys = []
    k_keys = []
    search_key = user.name + ':' + user.token + ':*'
    k_keys = rdb.keys(search_key)

    for k in k_keys:
        rsa = rdb.hget(k, 'rsa')
        title = rdb.hget(k, 'title')
        fingerprint = k.split(':')[3]
        res_pubkeys.append({'rsa':rsa, 'title':title, 'fingerprint':fingerprint})
    return res_pubkeys

def get_key(userid, rsa, title):
    user = User.get(userid)
    fingerprint = gen_fingerprint(rsa)
    k_rsakey = user.name + ':' + user.token + ':key:' + fingerprint
    rsakey = rdb.hget(k_rsakey, 'rsa')
    if rsakey == None:
        return False
    else:
        return True

def add_key(userid, rsa, title):
    user = User.get(userid)
    fingerprint = gen_fingerprint(rsa)

    k_rsakey = user.name + ':' + user.token + ':key:' + fingerprint

    rdb.hset(k_rsakey, "rsa", rsa)
    rdb.hset(k_rsakey, "title", title)

    return True
#    return redirect(url_for('ui.pubkeys'))

def get_key_by_userid(userid, keyfp):
    user = User.get(userid)
    k_key = user.name + ':' + user.token + ':key:' + keyfp
    rsa = rdb.hget(k_key, 'rsa')
    title = rdb.hget(k_key, 'title')
    return {'rsa':rsa, 'title':title, 'fingerprint':keyfp}

def delete_key_by_userid(userid, keyfp):
    user = User.get(userid)
    k_key = user.name + ':' + user.token + ':key:' + keyfp
    rdb.delete(k_key)
