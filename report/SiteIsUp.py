# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
load_dotenv()
import time
import requests

def sendMail():
    message = Mail(
        from_email=os.getenv('from_email'),
        to_emails=os.getenv('to_emails'),
        subject=f'{os.getenv('url')} is up!',
        html_content='<strong>Notification success!</strong>')
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
    except Exception as e:
        print('Error sending mail')

def siteDown():
    try:
        r = requests.get(os.getenv('url'), timeout=10)
        if r.status_code != 200:
            print('Site down')
            return True
        else:
            print('Site up')
            return False
    except Exception as e:
        print('Site down')
        return True

down = True

while down == True:
    time.sleep(5)
    down = siteDown()
    
sendMail()