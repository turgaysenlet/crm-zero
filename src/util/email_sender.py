import logging
import smtplib
from email.message import EmailMessage
import json

from pydantic import BaseModel

logging.basicConfig()
logger = logging.getLogger("EmailSender")
logger.setLevel(logging.DEBUG)

class EmailSender(BaseModel):
    sender_email: str
    app_password: str

    def __init__(self):
        creds = self.read_creadentials()
        sender_email = creds["email"]
        app_password = creds["app_password"]
        super().__init__(sender_email=sender_email, app_password=app_password)

    def send_mail(self, receiver_email: str, subject: str, body: str) -> EmailMessage:
        # Set up the message
        msg = EmailMessage()
        msg["From"] = self.sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.set_content(body)

        # Send using Gmail's SMTP server
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(self.sender_email, self.app_password)  # Use an App Password if using Gmail with 2FA
            smtp.send_message(msg)
            return msg

    def read_creadentials(self) -> dict:
        # Load credentials from file
        with open("credentials.json", "r") as f:
            creds = json.load(f)
            return creds
