# coding: utf-8

import os

DEBUG = True

MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'abc123')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'neptulon')

SQLALCHEMY_POOL_SIZE = 100
SQLALCHEMY_POOL_TIMEOUT = 10
SQLALCHEMY_POOL_RECYCLE = 2000

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_DB = int(os.getenv('REDIS_DB', '0'))

SECRET_KEY = os.getenv('SECRET_KEY', '69wolegeca')
SERVER_PORT = int(os.getenv('SERVER_PORT', '5000'))
SERVER_NAME = os.getenv('SERVER_NAME')

MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.exmail.qq.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', '465'))
MAIL_USE_TLS = bool(os.getenv('MAIL_USE_TLS', ''))
MAIL_USE_SSL = bool(os.getenv('MAIL_USE_SSL', '1'))
MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')

try:
    from .local_config import *
except ImportError:
    pass

SQLALCHEMY_DATABASE_URI = 'mysql://{0}:{1}@{2}:{3}/{4}'.format(
    MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE,
)

