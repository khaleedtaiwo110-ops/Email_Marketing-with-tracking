import imaplib
import email
import sqlite3

from db import get_connection


# ---------------- CHECK REPLIES ---------------- #
def check_replies_and_update(contacts, contact_list, sender_email, password):

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(sender_email, password)
        mail.select("inbox")

        status, messages = mail.search(None, 'UNSEEN')

        if status != "OK":
            return

        for num in messages[0].split():

            _, msg_data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            sender = msg.get("From", "").lower()

            # clean sender email extraction
            sender_email_clean = sender
            if "<" in sender and ">" in sender:
                sender_email_clean = sender.split("<")[1].split(">")[0].strip()

            for index, contact in enumerate(contacts):

                if contact["email"].lower() != sender_email_clean:
                    continue

                # ---------------- DB UPDATE ---------------- #
                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE contacts
                    SET replied = 1,
                        replied_at = datetime('now'),
                        status = 'replied'
                    WHERE email=?
                """, (contact["email"],))

                conn.commit()
                conn.close()

                # ---------------- MEMORY UPDATE ---------------- #
                contacts[index]["status"] = "replied"

                # ---------------- UI UPDATE (SAFE) ---------------- #
                def update_ui():
                    contact_list.delete(index)
                    contact_list.insert(
                        index,
                        f"{contact['company']} | {contact['email']} | REPLIED ✅"
                    )

                contact_list.after(0, update_ui)

                print(f"✅ Reply detected: {contact['email']}")

    except Exception as e:
        print("Reply check error:", e)