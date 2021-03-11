import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from Amazon import AmazonChecker 
from selenium import webdriver

from dotenv import load_dotenv
load_dotenv()

def sendMail(link):
    message = Mail(
        from_email=os.getenv('from_email'),
        to_emails=os.getenv('to_emails'),
        subject='%s is up!'%link,
        html_content='<strong>Add to cart success!</strong><br/>%s'%link)
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
    except Exception as e:
        print('Error sending mail')

driver = webdriver.Firefox()
links = os.getenv('links').split(";")
amazon = AmazonChecker(driver)
for link in links:
    success = amazon.checkAndBuy(link)
    print(success)
    if success:
        sendMail(link)
driver.close()