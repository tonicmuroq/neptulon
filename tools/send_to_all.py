# coding: utf-8

import sys
import os
sys.path.append(os.path.abspath('.'))

from flask import render_template
from flask.ext.mail import Message
from neptulon.ext import mail
from neptulon.config import MAIL_USERNAME, MAC_VPN_CONFIG_FILE, WIN_VPN_CONFIG_FILE
from neptulon.app import create_app
from neptulon.ext import db
from neptulon.models import User

def send_emails():
    with app.app_context():
        users, total = User.list_users(limit=2)
        for u in users:
            if u.id:
                if not u.send_doc_email():
                    print '!!! sending doc email error !!!'
            else:
                print 'uid error'
        print 'all emails have been sent.'

if __name__ == '__main__':
    app = create_app()
    send_emails()
