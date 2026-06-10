import sqlite3
import time
import random

from db import get_connection
from email_sender import send_email
from templates import (
    generate_followup_html,
    generate_followup2_html,
    generate_followup3_html,
    build_email
)


# ---------------- FOLLOW UP 1 ---------------- #
def run_followups(contacts, update_ui, sender_email, password, status_callback=None):
    print("🚀 Follow Up 1 Campaign Started")
    if status_callback: status_callback("🚀 Sequence 1 activated. Filtering opened warm leads...")

    try:
        processed_count = 0
        for index, c in enumerate(contacts):
            if c.get("status") != "sent" or c.get("opened") != 1:
                continue

            processed_count += 1
            company = c["company"]
            email = c["email"]

            if status_callback: status_callback(f"📨 Delivering Follow Up 1 to {company}")

            subject = f"Following up - {company}"
            html = generate_followup_html(company, email)
            msg = build_email(html, email)

            sent = send_email(sender_email, password, email, subject, msg)

            conn = get_connection()
            cursor = conn.cursor()

            if sent:
                status = "followup"
                cursor.execute("UPDATE contacts SET status=? WHERE email=?", (status, email))
                contacts[index]["status"] = status
                update_ui(index, c, status)

            conn.commit()
            conn.close()
            time.sleep(random.randint(5, 10))

        if status_callback:
            status_callback(f"✅ Sequence 1 finished. Processed {processed_count} warm entries.")

    except Exception as e:
        if status_callback: status_callback(f"❌ Follow Up 1 Failed: {str(e)}")


# ---------------- FOLLOW UP 2 ---------------- #
def run_followup2(contacts, update_ui, sender_email, password, status_callback=None):
    print("🚀 Follow Up 2 Campaign Started")
    if status_callback: status_callback("🚀 Sequence 2 activated. Checking active pipeline steps...")

    try:
        processed_count = 0
        for index, c in enumerate(contacts):
            if c.get("status") != "followup" or c.get("opened") != 1:
                continue

            processed_count += 1
            company = c["company"]
            email = c["email"]

            if status_callback: status_callback(f"📨 Delivering Follow Up 2 to {company}")

            subject = f"Quick check-in - {company}"
            html = generate_followup2_html(company, email)
            msg = build_email(html, email)

            sent = send_email(sender_email, password, email, subject, msg)

            conn = get_connection()
            cursor = conn.cursor()

            if sent:
                status = "followup2"
                cursor.execute("UPDATE contacts SET status=? WHERE email=?", (status, email))
                contacts[index]["status"] = status
                update_ui(index, c, status)

            conn.commit()
            conn.close()
            time.sleep(random.randint(5, 10))

        if status_callback:
            status_callback(f"✅ Sequence 2 finished. Processed {processed_count} active entries.")

    except Exception as e:
        if status_callback: status_callback(f"❌ Follow Up 2 Failed: {str(e)}")


# ---------------- FOLLOW UP 3 ---------------- #
def run_followup3(contacts, update_ui, sender_email, password, status_callback=None):
    print("🚀 Final Follow Up Campaign Started")
    if status_callback: status_callback("🚀 Final Sequence activated. Processing late-stage pipeline...")

    try:
        processed_count = 0
        for index, c in enumerate(contacts):
            if c.get("status") != "followup2" or c.get("opened") != 1:
                continue

            processed_count += 1
            company = c["company"]
            email = c["email"]

            if status_callback: status_callback(f"📨 Delivering Final Drop to {company}")

            subject = f"Final follow-up - {company}"
            html = generate_followup3_html(company, email)
            msg = build_email(html, email)

            sent = send_email(sender_email, password, email, subject, msg)

            conn = get_connection()
            cursor = conn.cursor()

            if sent:
                status = "completed"
                cursor.execute("UPDATE contacts SET status=? WHERE email=?", (status, email))
                contacts[index]["status"] = status
                update_ui(index, c, status)

            conn.commit()
            conn.close()
            time.sleep(random.randint(5, 10))

        if status_callback:
            status_callback(f"✅ Final Sequences completed. Processed {processed_count} pipeline completions.")

    except Exception as e:
        if status_callback: status_callback(f"❌ Final Follow Up Failed: {str(e)}")