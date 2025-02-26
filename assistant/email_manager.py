import imaplib
import smtplib
from email.message import EmailMessage
import os

class EmailManager:
    def __init__(self):
        self.connected = False
        
    def connect(self):
        try:
            self.mail = imaplib.IMAP4_SSL('imap.gmail.com')
            self.mail.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASS'))
            self.connected = True
        except Exception as e:
            return f"Connection failed: {str(e)}"

    def check_email(self):
        if not self.connected: self.connect()
        self.mail.select('inbox')
        _, data = self.mail.search(None, 'UNSEEN')
        return len(data[0].split())