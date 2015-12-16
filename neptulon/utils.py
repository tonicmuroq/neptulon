#!/usr/bin/python
#coding:utf-8

from functools import wraps
from flask import g, redirect, url_for, session

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


def paginator_kwargs(kw):
    d = kw.copy()
    d.pop('start', None)
    d.pop('limit', None)
    return d
