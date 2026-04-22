import sqlite3
import time
import random

from db import get_connection
from email_sender import send_email
from templates import (
    generate_followup_html,
    generate_followup2_html,
    generate_followup3_html
)

# NOTE: avoid importing root/contact_list directly if possible
# we pass UI callbacks instead (safer)


# ---------------- FOLLOW UP 1 ---------------- #
def run_followups(contacts, update_ui, sender_email, password, progress_label=None):

    for index, c in enumerate(contacts):

        if c.get("status") != "sent":
            continue

        company = c["company"]
        email = c["email"]

        if progress_label:
            progress_label.config(text=f"Sending follow-up 1 to {company}")

        subject = f"Following up - {company}"
        msg = generate_followup_html(company, email)

        sent = send_email(sender_email, password, email, subject, msg)

        conn = get_connection()
        cursor = conn.cursor()

        if sent:
            status = "followup"

            cursor.execute(
                "UPDATE contacts SET status=? WHERE email=?",
                (status, email)
            )

            contacts[index]["status"] = status
            update_ui(index, c, status)

        conn.commit()
        conn.close()

        time.sleep(random.randint(5, 10))


# ---------------- FOLLOW UP 2 ---------------- #
def run_followup2(contacts, update_ui, sender_email, password, progress_label=None):

    for index, c in enumerate(contacts):

        if c.get("status") != "followup":
            continue

        company = c["company"]
        email = c["email"]

        if progress_label:
            progress_label.config(text=f"Sending follow-up 2 to {company}")

        subject = f"Quick Check-In - {company}"
        msg = generate_followup2_html(company, email)

        sent = send_email(sender_email, password, email, subject, msg)

        conn = get_connection()
        cursor = conn.cursor()

        if sent:
            status = "followup2"

            cursor.execute(
                "UPDATE contacts SET status=? WHERE email=?",
                (status, email)
            )

            contacts[index]["status"] = status
            update_ui(index, c, status)

        conn.commit()
        conn.close()

        time.sleep(random.randint(5, 10))


# ---------------- FOLLOW UP 3 ---------------- #
def run_followup3(contacts, update_ui, sender_email, password, progress_label=None):

    for index, c in enumerate(contacts):

        if c.get("status") != "followup2":
            continue

        company = c["company"]
        email = c["email"]

        if progress_label:
            progress_label.config(text=f"Final follow-up to {company}")

        subject = f"Final follow-up - {company}"
        msg = generate_followup3_html(company, email)

        sent = send_email(sender_email, password, email, subject, msg)

        conn = get_connection()
        cursor = conn.cursor()

        if sent:
            status = "completed"

            cursor.execute(
                "UPDATE contacts SET status=? WHERE email=?",
                (status, email)
            )

            contacts[index]["status"] = status
            update_ui(index, c, status)

        conn.commit()
        conn.close()

        time.sleep(random.randint(5, 10))