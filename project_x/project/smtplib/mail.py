import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

email_sender = 'gulmirabakhytbekovna@gmail.com'
password = 'fqjmyryuohuhrjko'


smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
smtp_server.starttls()
smtp_server.login(email_sender, password)


def send_mail(mail, code):
    msg = MIMEMultipart()
    msg.attach(MIMEText(f'Ваш код: {code}'))
    email_getter = mail
    smtp_server.sendmail(email_sender, email_getter, msg.as_string())
