# coding: utf-8

from werkzeug.security import gen_salt

from neptulon.ext import db
from neptulon.models.base import Base
from neptulon.models.user import User


class Client(Base):

    __tablename__ = 'client'

    name = db.Column(db.String(255))
    client_id = db.Column(db.String(40), index=True)
    client_secret = db.Column(db.String(60))
    _redirect_uris = db.Column(db.Text)
    _default_scopes = db.Column(db.Text)

    @classmethod
    def create(cls, name, redirect_uris, default_scopes):
        client = cls(
            name=name,
            client_id=gen_salt(40),
            client_secret=gen_salt(60),
            _redirect_uris=' '.join(redirect_uris),
            _default_scopes=' '.join(default_scopes)
        )
        db.session.add(client)
        db.session.commit()
        return client

    @classmethod
    def get_by_client_id(cls, client_id):
        return cls.query.filter_by(client_id=client_id).first()

    @classmethod
    def get_all(cls, start=0, limit=20):
        q = cls.query.order_by(cls.id.desc())
        return q[start:start+limit]

    @property
    def client_type(self):
        return 'public'

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    def delete(self):
        Token.delete_by_client(self.client_id)
        super(Client, self).delete()


class Grant(Base):

    __tablename__ = 'grant'
    __table_args__ = (
        db.Index('code_client', 'code', 'client_id'),
    )

    user_id = db.Column(db.Integer)
    client_id = db.Column(db.String(40))
    code = db.Column(db.String(255))
    redirect_uri = db.Column(db.String(255))
    expires = db.Column(db.DateTime)
    _scopes = db.Column(db.Text)

    @classmethod
    def create(cls, user_id, client_id, code, redirect_uri, scopes, expires):
        grant = cls(
            user_id=user_id,
            client_id=client_id,
            code=code,
            redirect_uri=redirect_uri,
            _scopes=' '.join(scopes),
            expires=expires
        )
        db.session.add(grant)
        db.session.commit()
        return grant

    @classmethod
    def get_by_code_and_client(cls, code, client_id):
        return cls.query.filter_by(code=code, client_id=client_id).first()

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []

    @property
    def client(self):
        return Client.get_by_client_id(self.client_id)

    @property
    def user(self):
        return User.get(self.user_id)


class Token(Base):

    __tablename__ = 'token'
    __table_args__ = (
        db.Index('user_client', 'user_id', 'client_id'),
    )

    client_id = db.Column(db.String(40), index=True)
    user_id = db.Column(db.Integer)
    token_type = db.Column(db.String(40))

    access_token = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(255), unique=True)
    expires = db.Column(db.DateTime)
    _scopes = db.Column(db.Text)

    @classmethod
    def create(cls, client_id, user_id, token_type, access_token, refresh_token, expires, scopes):
        token = cls(
            client_id=client_id,
            user_id=user_id,
            token_type=token_type,
            access_token=access_token,
            refresh_token=refresh_token,
            expires=expires,
            _scopes=scopes,
        )
        db.session.add(token)
        db.session.commit()
        return token

    @classmethod
    def get_by_access(cls, access_token):
        return cls.query.filter_by(access_token=access_token).first()

    @classmethod
    def get_by_refresh(cls, refresh_token):
        return cls.query.filter_by(refresh_token=refresh_token).first()

    @classmethod
    def get_by_user(cls, user_id, start=0, limit=20):
        q = cls.query.filter_by(user_id=user_id)
        return q[start:start+limit]

    @classmethod
    def delete_by_client_and_user(cls, client_id, user_id):
        cls.query.filter_by(user_id=user_id, client_id=client_id).delete()
        db.session.commit()

    @classmethod
    def delete_by_client(cls, client_id):
        cls.query.filter_by(client_id=client_id).delete()
        db.session.commit()

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []

    @property
    def user(self):
        return User.get(self.user_id)

    @property
    def client(self):
        return Client.get_by_client_id(self.client_id)
