
#   EMAIL operation Function 

from email.mime.text import MIMEText
import logging
import smtplib
from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
logger = logging.getLogger(__name__)
def send_mail(email_args:object):
    SMTP_USER = getattr(settings,'SMTP_USER',None)
    SMTP_PASSWORD = getattr(settings,'SMTP_PASSWORD',None)
    SMTP_SERVER = getattr(settings,'SMTP_SERVER',None)
    SMTP_PORT = getattr(settings,'SMTP_PORT',None)
    FORMAT_ADDER = getattr(settings,'FORMAT_ADDER',None)
    try:
        logger.info("Sending Email .......")
        to_email = email_args["to"] 
        subject = email_args["subject"]
        body = email_args["body"]
        
        message = MIMEMultipart()
        message["From"] = formataddr((FORMAT_ADDER,SMTP_USER))
        message["To"] = to_email
        message["subject"] = subject
        message.attach(MIMEText(body,"html"))   
        print(F"Sending Email ....... {to_email}")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20) as server:
            server.ehlo()              # 1️⃣ identify client
            server.starttls()          # 2️⃣ 🔥 REQUIRED for Gmail
            server.ehlo()              # 3️⃣ re-identify after TLS
            server.login(SMTP_USER, SMTP_PASSWORD)  # 4️⃣ auth
            server.send_message(message) 
            print("Email sent successfully")
        # with smtplib.SMTP(SMTP_SERVER,SMTP_PORT) as server:
        #     server.ehlo()
        #     server.send_message(message)
        logger.info("All Emails sent successfully")
        return True
    except Exception as e:
        print(f"Email Sending Error :: {e}")
        logger.exception(f"Email Sending Error :: {e}")
        return False
        
        
    