from flask_mail import Message
from __init__ import mail
import os
from flask import  render_template


def send_email(user):

    token = user.get_reset_token()

    msg = Message()
    msg.subject = "Privacy Guard Password Reset"
    msg.sender = os.getenv('MAIL_USERNAME')
    msg.recipients = [user.email]
    msg.html = render_template('reset_email.html', user=user, token=token)

    mail.send(msg)
