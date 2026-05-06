import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(sender_email, app_password, to_email, subject, msg):
    try:
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=60) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, to_email, msg.as_string())

        print(f"✅ Sent to {to_email}")
        return True

    except Exception as e:
        print(f"[EMAIL ERROR] {to_email} -> {e}")
        return False