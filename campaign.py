import time
import random
from db import get_connection
from email_sender import send_email
from templates import generate_email_html


def run_campaign(contacts, update_ui, sender_email, password):
    print("🚀 Campaign started")

    try:
        for c in contacts:
            c["status"] = "pending"

        for index, c in enumerate(contacts):
            print("➡️ Processing:", c)

            subject = f"Travel Support for {c['company']}"
            msg = generate_email_html(c["company"], c["email"])

            # ---------------- SEND EMAIL ---------------- #
            sent = send_email(sender_email, password, c["email"], subject, msg)
            print("Email sent result:", sent)

            # ---------------- DB UPDATE ---------------- #
            conn = get_connection()
            cursor = conn.cursor()

            status = "sent" if sent else "failed"

            cursor.execute("""
                UPDATE contacts 
                SET status=?, sent_at=CASE WHEN ?='sent' THEN datetime('now') ELSE sent_at END
                WHERE email=?
            """, (status, status, c["email"]))

            conn.commit()
            conn.close()

            # ---------------- SAFE UI UPDATE ---------------- #
            contacts[index]["status"] = status
            update_ui(index, c, status)

            time.sleep(random.randint(5, 10))

    except Exception as e:
        print("❌ CAMPAIGN ERROR:", e)