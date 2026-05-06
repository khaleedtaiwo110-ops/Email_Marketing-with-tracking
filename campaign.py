import email
import time
import random
from db import get_connection
from email_sender import send_email
from templates import generate_email_html, build_email


def run_campaign(contacts, update_ui, sender_email, password, company=None):
    print("🚀 Campaign started")

    try:
        for c in contacts:
            c["status"] = "pending"

        for index, c in enumerate(contacts):
            print("➡️ Processing:", c)

            subject = f"Travel Support for {c['company']}"

            # ✅ FIX 1: use correct email
            html = generate_email_html(c["company"], c["email"])

            # ✅ FIX 2: build full message (with tracking pixel)
            msg = build_email(html, c["email"])

            # ✅ FIX 3: send full MIME message
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

            # ---------------- UI UPDATE ---------------- #
            contacts[index]["status"] = status
            update_ui(index, c, status)

            time.sleep(random.randint(5, 10))

    except Exception as e:
        print("Campaign error:", e)