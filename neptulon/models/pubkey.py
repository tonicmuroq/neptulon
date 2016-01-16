# coding: utf-8
from neptulon.config import rdb
from neptulon.models import User

class Pubkey:

    def __init__(self, rsa, title, fingerprint):
        self.rsa = rsa
        self.title = title
        self.fingerprint = fingerprint


