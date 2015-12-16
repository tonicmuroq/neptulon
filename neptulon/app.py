# coding: utf-8

import logging

from flask import Flask, g, request, session
from werkzeug.utils import import_string

from neptulon.models import User
from neptulon.utils import paginator_kwargs

from .ext import db

blueprints = [
    'ui',
    'auth',
    'index',
    'admin',
]

def create_app():
    app = Flask(__name__, static_url_path='/neptulon/static')
    app.config.from_object('neptulon.config')
    app.secret_key = app.config['SECRET_KEY']

    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s', level=logging.INFO)

    db.init_app(app)

    for bp in blueprints:
        import_name = '%s.views.%s:bp' % (__package__, bp)
        app.register_blueprint(import_string(import_name))

    for fl in (max, min, paginator_kwargs):
        app.add_template_global(fl)

    @app.before_request
    def init_global_vars():
        g.user = None
        if 'id' in session:
            g.user = User.get(session['id'])
        g.redir = request.args.get('redirect', '')
        g.start = request.args.get('start', type=int, default=0)
        g.limit = request.args.get('limit', type=int, default=20)

    return app
