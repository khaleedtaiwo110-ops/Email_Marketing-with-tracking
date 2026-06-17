import email
import time
import random
import os
from db import get_connection
from email_sender import send_email
from templates import generate_email_html, build_email


def run_campaign(contacts, update_ui, sender_email, password, status_callback=None):
    print("🚀 Campaign started")
    if status_callback:
        status_callback("🚀 Campaign engine initialized. Processing lead array...")

    try:
        # Define path to your corporate review document
        pdf_path = "corporate_review.pdf"
        if not os.path.exists(pdf_path):
            if status_callback:
                status_callback(
                    "⚠️ Warning: 'corporate_review.pdf' not found in project folder. Sending without attachment.")
            pdf_path = None

        for index, c in enumerate(contacts):
            # 🎯 Skip contacts who have already been processed or moved forward
            if c.get("status") in ["sent", "followup", "followup2", "completed", "replied"]:
                print(f"⏭️ Skipping {c['company']} (Status is already {c['status']})")
                continue

            print("➡️ Processing:", c)
            if status_callback:
                status_callback(f"➡️ Processing row {index + 1}: {c['company']}")

            subject = f"Optimizing {c['company']}'s corporate mobility / Project timeline protection"

            # Generate template and wrap content structure
            html = generate_email_html(c["company"], c["email"], c.get("first_name"))
            msg = build_email(html, c["email"], attachment_path=pdf_path)

            # Execute delivery sequence
            sent = send_email(sender_email, password, c["email"], subject, msg)
            print("Email sent result:", sent)

            # ---------------- 🛠️ FIXED DB UPDATE ---------------- #
            conn = get_connection()
            cursor = conn.cursor()

            status = "sent" if sent else "failed"

            # Execute explicit targeted status write for the active lead!
            cursor.execute(
                "UPDATE contacts SET status = ?, sent_at = datetime('now') WHERE email = ?",
                (status, c["email"])
            )

            conn.commit()
            conn.close()

            # ---------------- MEMORY & UI UPDATE ---------------- #
            from Email_Marketing import contacts_lock

            with contacts_lock:
                if index < len(contacts) and contacts[index]["email"] == c["email"]:
                    contacts[index]["status"] = status

            # Safe asynchronous update execution back to the Tkinter view loop
            update_ui(index, c, status)

            if status_callback:
                status_callback(f"✅ Status updated for {c['company']} -> {status.upper()}")

            # Polite anti-spam timing throttle interval
            time.sleep(random.randint(5, 10))

        if status_callback:
            status_callback("📋 Initial campaign run complete. Clean pipeline targets processed.")

    except Exception as e:
        print(f"[FATAL ENGINE ERROR] {e}")
        if status_callback:
            status_callback(f"❌ Campaign halted due to fatal exception: {e}")