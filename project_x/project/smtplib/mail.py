import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

email_sender = 'arystanbek.abdrakhmanov@gmail.com'
password = 'kfkoogzwebjdvisk'


smtp_server = smtplib.SMTP('smtp.gmail.com', 587)

def send_mail(mail, code):
    try:
        smtp_server.login(email_sender, password)
        msg = MIMEMultipart()
        msg.attach(MIMEText(f'Ваш код: {code}'))
        email_getter = mail
        smtp_server.sendmail(email_sender, email_getter, msg.as_string())
    finally:
        smtp_server.quit()
