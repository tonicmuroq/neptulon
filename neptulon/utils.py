# coding:utf-8

import json
import base64
import hashlib
from functools import wraps
from flask import g, redirect, url_for, session, request, Response


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


def jsonize(f):
    @wraps(f)
    def _(*args, **kwargs):
        r = f(*args, **kwargs)
        data, code = r if isinstance(r, tuple) else (r, 200)
        return Response(json.dumps(data), status=code, mimetype='application/json')
    return _
