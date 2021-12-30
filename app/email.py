from email.mime import text
from flask.templating import render_template
from flask_mail import Message
from config import Config
from . import mail
import smtplib
from flask import current_app
from email.message import EmailMessage

def send_email(to, subject, template, **kwargs): 
    server = smtplib.SMTP_SSL()
    textfile = render_template(template + '.txt', **kwargs)
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = current_app.config['MAIL_USERNAME']
    msg['To'] = to
    server = smtplib.SMTP_SSL('smtp.qq.com', current_app.config['MAIL_PORT'])
    server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
    
    msg.set_content(textfile)
    server.send_message(msg)
    
    server.quit()