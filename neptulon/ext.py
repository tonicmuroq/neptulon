# coding: utf-8

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask.ext.oauthlib.provider import OAuth2Provider
from neptulon.config import REDIS_HOST, REDIS_PORT, REDIS_DB
import redis


db = SQLAlchemy()
mail = Mail()
oauth = OAuth2Provider()
redisPool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
rdb = redis.Redis(connection_pool=redisPool)
