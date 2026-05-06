import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(sender_email, app_password, to_email, subject, html):
    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html, "html"))

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=60)
         
        # server.set_debuglevel(1)  # 👈 VERY IMPORTANT

        print("➡️ Connecting...")
        server.login(sender_email, app_password)
        print("✅ Logged in")

        server.sendmail(sender_email, to_email, msg.as_string())
        print("✅ Email sent")

        server.quit()
        return True

    except Exception as e:
        print(f"[EMAIL ERROR] {to_email} -> {e}")
        return False