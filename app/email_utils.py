import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .celery_app import celery_app
from .config import MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM, MAIL_PORT, MAIL_SERVER


@celery_app.task(name='send_email_task')
def send_email_task(email_to: str, subject: str, body: str):

    msg = MIMEMultipart()
    msg['From'] = MAIL_FROM
    msg['To'] = email_to
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(MAIL_FROM, email_to, msg.as_string())

    except Exception as e:
        print(f"Failed to send email: {e}")