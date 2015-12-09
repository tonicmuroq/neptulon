# coding: utf-8

import logging

from flask import Flask
from werkzeug.utils import import_string

from .ext import db

blueprints = [
    'ui',
    'auth',
    'index',
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

    return app
