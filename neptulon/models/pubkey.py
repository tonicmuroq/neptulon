# coding: utf-8

import datetime
import sqlalchemy.exc

from neptulon.ext import db
from neptulon.utils import gen_fingerprint
from neptulon.models.base import Base

class RSAKey(Base):

    user_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    rsa = db.Column(db.Text, nullable=False)
    fingerprint = db.Column(db.String(32), nullable=False)
    time = db.Column(db.DateTime, default=datetime.datetime.now)
    
    @classmethod
    def create(cls, user_id, title, rsa):
        fingerprint = gen_fingerprint(rsa)
        try:
            rsakey = cls(user_id=user_id, title=title, rsa=rsa, fingerprint=fingerprint)
            db.session.add(rsakey)
            db.session.commit()
            return rsakey
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
            return None

    @classmethod
    def get_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()

    @classmethod
    def get_by_fingerprint(cls, fingerprint):
        return cls.query.filter_by(fingerprint=fingerprint).first()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
