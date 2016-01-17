# coding: utf-8
import datetime
import sqlalchemy.exc
from neptulon.ext import db, rdb
from neptulon.models import User
from neptulon.utils import gen_fingerprint
from neptulon.models.base import Base

class RSAKey(Base):

    user_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    rsa = db.Column(db.String(2000), nullable=False)
    fingerprint = db.Column(db.String(32), nullable=False)
    time = db.Column(db.DateTime, default=datetime.datetime.now)
    
    @classmethod
    def create(cls, userid, title, rsa):
        fingerprint = gen_fingerprint(rsa)
        try:
            rsakey = cls(user_id=userid, title=title, rsa=rsa, fingerprint=fingerprint)
            db.session.add(rsakey)
            db.session.commit()
            return True
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
            return False

    @classmethod
    def get_by_userid(cls, userid):
        return cls.query.filter_by(user_id=userid).first()

    @classmethod
    def get_by_fingerprint(cls, fingerprint):
        return cls.query.filter_by(fingerprint=fingerprint).first()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
