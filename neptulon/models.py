# coding: utf-8

import datetime
import sqlalchemy.exc
from sqlalchemy.ext.declarative import declared_attr
from werkzeug.security import gen_salt, generate_password_hash, check_password_hash

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
    real_name = db.Column(db.String(255), unique=True, nullable=False, default='')
    password = db.Column(db.String(255), nullable=False, default='')
    privilege = db.Column(db.Integer, default=0)
    time = db.Column(db.DateTime, default=datetime.datetime.now)

    @classmethod
    def create(cls, name, email, password, real_name):
        try:
            u = cls(name=name, email=email, real_name=real_name)
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

    @classmethod
    def list_users(cls, start=0, limit=20):
        q = cls.query.order_by(cls.id.desc())
        total = q.count()
        q = q.offset(start)
        if limit is not None:
            q = q.limit(limit)
        return q.all(), total

    def set_password(self, password):
        self.password = generate_password_hash(password)
        db.session.add(self)
        db.session.commit()

    def sudo(self):
        self.privilege = 1 if not self.privilege else 0
        db.session.add(self)
        db.session.commit()

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_auths(self):
        return Auth.query.filter_by(user_id=self.id).order_by(Auth.id.desc()).all()

    def to_dict(self):
        return {'name': self.name, 'email': self.email}

    def delete(self):
        db.session.delete(self)
        db.session.commit()


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
