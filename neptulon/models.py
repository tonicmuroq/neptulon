# coding: utf-8

import bcrypt
import datetime
import sqlalchemy.exc
from sqlalchemy.ext.declarative import declared_attr
from werkzeug.security import gen_salt

from .ext import db


def _utf8(s):
    if isinstance(s, unicode):
        return s.encode('utf-8')
    return s


class Base(db.Model):

    __abstract__ = True

    @declared_attr
    def id(cls):
        return db.Column('id', db.Integer, primary_key=True, autoincrement=True)

    @classmethod
    def get(cls, id):
        return cls.query.filter(cls.id == id).first()

    @classmethod
    def get_multi(cls, ids):
        return [cls.get(i) for i in ids]


class User(Base):

    __tablename__ = 'user'

    name = db.Column(db.String(255), unique=True, nullable=False, default='')
    email = db.Column(db.String(255), unique=True, nullable=False, default='')
    password = db.Column(db.String(255), nullable=False, default='')
    privilege = db.Column(db.Integer, default=0)
    time = db.Column(db.DateTime, default=datetime.datetime.now)

    @classmethod
    def create(cls, name, email, password):
        try:
            u = cls(name=name, email=email)
            db.session.add(u)
            db.session.commit()
            u.set_password(password)
            return u
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
            return None

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def set_password(self, password):
        self.password = bcrypt.hashpw(_utf8(password), bcrypt.gensalt(8))
        db.session.add(self)
        db.session.commit()

    def check_password(self, password):
        if not (password and self.password):
            return False
        return bcrypt.hashpw(_utf8(password), _utf8(self.password)) == self.password

    def get_auths(self):
        return Auth.query.filter_by(user_id=self.id).order_by(Auth.id.desc()).all()

    def to_dict(self):
        return {'name': self.name, 'email': self.email}


class Auth(Base):

    __tablename__ = 'auth'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'url'),
    )

    url = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    token = db.Column(db.String(64), default=lambda: gen_salt(64))
    time = db.Column(db.DateTime, default=datetime.datetime.now)

    @classmethod
    def get_or_create(cls, user_id, url):
        auth = cls.get_by_user_and_url(user_id, url)
        if auth:
            return auth
        try:
            auth = cls(user_id=user_id, url=url)
            db.session.add(auth)
            db.session.commit()
            return auth
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
            return None

    @classmethod
    def get_by_user_and_url(cls, user_id, url):
        return cls.query.filter_by(user_id=user_id, url=url).first()

    @classmethod
    def get_by_token(cls, token):
        return cls.query.filter_by(token=token).first()

    @property
    def user(self):
        return User.get(self.user_id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
