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


def send_email(user):
    message = Message(
                subject=u'用户使用向导',
                sender=MAIL_USERNAME,
                recipients=[user.email]
            )
    message.html = render_template('/email/guide.html', user=user)
    with open(MAC_VPN_CONFIG_FILE) as f:
        message.attach('nova.zip', 'application/octet-stream', f.read())
    with open(WIN_VPN_CONFIG_FILE) as f:
        message.attach('ikev2vpn.zip', 'application/octet-stream', f.read())
    mail.send(message)


def send_emails():
    with app.app_context():
        users, total = User.list_users()
        for u in users:
            send_email(u)
        print 'all emails have been sent.'

if __name__ == '__main__':
    app = create_app()
    send_emails()
