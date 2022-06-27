from flask_mail import Mail, Message
from flask import current_app, render_template
from threading import Thread
from logging import getLogger

logger = getLogger('gunicorn.error')
mailer = Mail()


def send_async_email(app, msg):
    with app.app_context():
        mailer.send(msg)
        logger.info('Email sent to users mailbox by thread')

def send_email(to, subject, template, **kwargs):
    if type(to) != list:
        raise TypeError('To most be a list')
        
    msg = Message(subject, recipients = to)
    msg.html = template
    logger.info('sending email ...')
    thr = Thread(target = send_async_email, args=[current_app._get_current_object(), msg])
    thr.start()

    

