import email
import time
import random
from db import get_connection
from email_sender import send_email
from templates import generate_email_html, build_email

def run_campaign(contacts, update_ui, sender_email, password, company=None):
    print("🚀 Campaign started")

    try:
        # DO NOT reset statuses to pending here!
        # Removing that loop preserves existing statuses ('sent', 'failed', etc.)

        for index, c in enumerate(contacts):
            # 🚀 CRITICAL FIX: Skip anyone who is NOT pending!
            if c.get("status") != "pending":
                print(f"⏭️ Skipping {c['email']} - Already processed (Status: {c['status']})")
                continue

            print("➡️ Processing:", c)

            subject = f"Travel Support for {c['company']}"
            html = generate_email_html(c["company"], c["email"])
            msg = build_email(html, c["email"])

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