# coding: utf-8

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask.ext.oauthlib.provider import OAuth2Provider


db = SQLAlchemy()
mail = Mail()
oauth = OAuth2Provider()
