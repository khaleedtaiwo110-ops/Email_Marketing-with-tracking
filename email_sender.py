import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(sender_email, app_password, to_email, subject, html):

    try:
        # 1. Create email container
        msg = MIMEMultipart()

        # 2. Set headers
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject

        # 3. Attach HTML correctly (IMPORTANT)
        msg.attach(MIMEText(html, "html"))

        # 4. Connect to Gmail SMTP
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
        server.starttls()
        server.login(sender_email, app_password)

        # 5. SEND (IMPORTANT FIX)
        server.sendmail(sender_email, to_email, msg.as_string())

        server.quit()

        return True

    except Exception as e:
        print(f"[EMAIL ERROR] {to_email} -> {e}")
        return False