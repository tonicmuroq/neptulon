# coding: utf-8

import datetime
import sqlalchemy.exc
from werkzeug.security import gen_salt, generate_password_hash, check_password_hash

from flask import render_template
from neptulon.ext import db
from neptulon.models.base import Base
from neptulon.models.pubkey import RSAKey
from flask.ext.mail import Message
from neptulon.ext import mail
from neptulon.config import MAIL_USERNAME, MAC_VPN_CONFIG_FILE, WIN_VPN_CONFIG_FILE


class User(Base):

    name = db.Column(db.String(255), unique=True, nullable=False, default='')
    email = db.Column(db.String(255), unique=True, nullable=False, default='')
    real_name = db.Column(db.String(255), unique=True, nullable=False, default='')
    password = db.Column(db.String(255), nullable=False, default='')
    token = db.Column(db.String(64), default=lambda: gen_salt(5), index=True)
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
    def get_by_token(cls, token):
        return cls.query.filter_by(token=token).first()

    @classmethod
    def list_users(cls, start=0, limit=20, admin=None):
        if admin:
            q = cls.query.filter_by(privilege=1).order_by(cls.id.desc())
        else:
            q = cls.query.order_by(cls.id.desc())
        total = q.count()
        q = q.offset(start)
        if limit is not None:
            q = q.limit(limit)
        return q.all(), total

    @property
    def pubkey(self):
        key = RSAKey.get_by_user_id(self.id)
        return key and key.rsa or ''

    def edit(self, name, email, password, real_name):
        if password:
            self.password = generate_password_hash(password)
        self.name = name
        self.email = email
        self.real_name = real_name
        db.session.add(self)
        db.session.commit()

    def set_password(self, password):
        self.password = generate_password_hash(password)
        db.session.add(self)
        db.session.commit()

    def refresh_token(self):
        self.token = gen_salt(5)
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

    def to_dict(self, private=False):
        d = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'real_name': self.real_name,
            'privilege': self.privilege,
        }
        if private:
            d['token'] = self.token
            d['pubkey'] = self.pubkey
        return d

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def send_doc_email(self):
        message = Message(
                    subject=u'翻墙账号及Surge网络配置使用说明',
                    sender=MAIL_USERNAME,
                    recipients=[self.email])
        message.html = render_template('/email/guide.html', user=self)
        with open(MAC_VPN_CONFIG_FILE) as f:
            message.attach('nova.zip', 'application/octet-stream', f.read())
        with open(WIN_VPN_CONFIG_FILE) as f:
            message.attach('ikev2vpn.zip', 'application/octet-stream', f.read())
        message.attach('surge.conf', 'application/octet-stream', render_template('/surge-template.conf', username=self.name, password=self.token))
        message.attach('ricebook.mobileconfig', 'application/octet-stream', render_template('/ricebook-template.mobileconfig', username=self.name, password=self.token))
        try:
            mail.send(message)
        except:
            return False
        return True

class Auth(Base):

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
