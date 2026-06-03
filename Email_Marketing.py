import threading
import tkinter as tk
from tkinter import messagebox
import os
import requests

from campaign import run_campaign
from db import init_db, get_connection
from followups import run_followups, run_followup2, run_followup3
from reply_tracker import check_replies_and_update

# ---------------- SETTINGS ---------------- #
SENDER_EMAIL = os.getenv("SENDER_EMAIL","viewtriptravels.co@gmail.com")
APP_PASSWORD = os.getenv("Gmail_app", "enni yjfi wwmj cgru")

contacts = []
contacts_lock = threading.Lock()

# ---------------- INIT DB ---------------- #
init_db()

# ---------------- LOAD CONTACTS ---------------- #
def load_contacts():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT company, email, website, status FROM contacts")
    rows = cursor.fetchall()

    with contacts_lock:
        contacts.clear()

        for row in rows:
            contacts.append({
                "company": row[0],
                "email": row[1],
                "website": row[2],
                "status": row[3]
            })

    conn.close()

# ---------------- ADD COMPANY ---------------- #
def add_company():
    company = company_entry.get().strip()
    email = email_entry.get().strip()
    website = website_entry.get().strip()

    if not company or not email:
        messagebox.showwarning("Missing info", "Company and email required")
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO contacts (company, email, website, status) VALUES (?, ?, ?, ?)",
            (company, email, website, "pending")
        )
        conn.commit()
        conn.close()

        with contacts_lock:
            contacts.append({
                "company": company,
                "email": email,
                "website": website,
                "status": "pending"
            })

        contact_list.insert(tk.END, f"{company} | {email} | PENDING")

        company_entry.delete(0, tk.END)
        email_entry.delete(0, tk.END)
        website_entry.delete(0, tk.END)

    except Exception as e:
        messagebox.showerror("Error", str(e))

# ---------------- DELETE COMPANY ---------------- #
def delete_company():
    selected = contact_list.curselection()

    if not selected:
        return

    index = int(selected[0])  # 🔥 FORCE INT TYPE

    with contacts_lock:
        email = contacts[index]["email"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM contacts WHERE email=?", (email,))
    conn.commit()
    conn.close()

    with contacts_lock:
        contacts.pop(index)

    contact_list.delete(index)

# ---------------- UPDATE UI ---------------- #
def update_ui(index, contact, status):
    def _update():
        contact_list.delete(index)
        contact_list.insert(
            index,
            f"{contact['company']} | {contact['email']} | {status.upper()}"
        )

    root.after(0, _update)

# ---------------- CAMPAIGN ---------------- #
def start_campaign():
    print("Start button clicked")
    threading.Thread(
        target=run_campaign,
        args=(contacts, update_ui, SENDER_EMAIL, APP_PASSWORD),
        daemon=True
    ).start()

# ---------------- FOLLOW UPS ---------------- #
def start_followups():
    threading.Thread(
        target=run_followups,
        args=(contacts, update_ui, SENDER_EMAIL, APP_PASSWORD),
        daemon=True
    ).start()

def start_followup2():
    threading.Thread(
        target=run_followup2,
        args=(contacts, update_ui, SENDER_EMAIL, APP_PASSWORD),
        daemon=True
    ).start()

def start_followup3():
    threading.Thread(
        target=run_followup3,
        args=(contacts, update_ui, SENDER_EMAIL, APP_PASSWORD),
        daemon=True
    ).start()

# ---------------- REPLY TRACKER ---------------- #
def auto_check_replies():
    try:
        check_replies_and_update(
            contacts,
            contact_list,
            SENDER_EMAIL,
            APP_PASSWORD
        )
    except Exception as e:
        print("Reply tracker error:", e)

    root.after(15000, auto_check_replies)

# ---------------- ANALYTICS ---------------- #
# ---------------- REAL TIME LOCAL STATS SYNCHRONIZER ---------------- #
def show_stats():
    def fetch_stats_worker():
        try:
            root.title("📊 Synchronizing metrics with server...")

            # Fetch the list of unique opened emails from Render
            response = requests.get("https://email-marketing-with-tracking.onrender.com/stats", timeout=30)

            if response.status_code == 200:
                cloud_data = response.json()
                opened_list = cloud_data.get("opened_emails", [])
                # Normalize emails to lowercase
                opened_set = {email.lower().strip() for email in opened_list}

                # Connect to your local actual DB to sync and calculate accurate metrics
                conn = get_connection()
                cursor = conn.cursor()

                # 1. Update your local database if an email was tracked in the cloud
                for email in opened_set:
                    cursor.execute("UPDATE contacts SET opened = 1 WHERE LOWER(email) = ?", (email,))
                conn.commit()

                # 2. Query total sent numbers from your local baseline
                cursor.execute("SELECT COUNT(*) FROM contacts WHERE status != 'pending'")
                total_sent = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM contacts WHERE opened = 1")
                total_opened = cursor.fetchone()[0]

                conn.close()

                # Refresh local UI memory and application list view
                load_contacts()
                root.after(0, update_contact_list_view)

                # Present accurate, calibrated local math
                messagebox.showinfo(
                    "Real Campaign Metrics",
                    f"Total Emails Sent: {total_sent}\n"
                    f"Verified Unique Opens: {total_opened}\n"
                    f"Estimated Open Rate: {((total_opened / total_sent) * 100) if total_sent > 0 else 0:.1f}%"
                )
            else:
                messagebox.showerror("Sync Error", f"Server dropped response code: {response.status_code}")

        except Exception as e:
            messagebox.showerror("Network Sync Failure", f"Could not sync data pipeline:\n{e}")
        finally:
            root.title("Email Marketing System")

    threading.Thread(target=fetch_stats_worker, daemon=True).start()


def update_contact_list_view():
    """Helper utility to make sure the Tkinter listbox shows modified open checkmarks instantly."""
    contact_list.delete(0, tk.END)
    for c in contacts:
        status_text = c.get('status', 'pending').upper()
        contact_list.insert(tk.END, f"{c['company']} | {c['email']} | {status_text}")


# ---------------- GUI ---------------- #
root = tk.Tk()
root.title("Viewtrip Outreach System")
root.geometry("900x700")

tk.Label(root, text="Viewtrip Outreach System", font=("Arial", 18)).pack(pady=10)

# FORM
form_frame = tk.Frame(root)
form_frame.pack()

tk.Label(form_frame, text="Company").grid(row=0, column=0)
tk.Label(form_frame, text="Email").grid(row=1, column=0)
tk.Label(form_frame, text="Website").grid(row=2, column=0)

company_entry = tk.Entry(form_frame, width=30)
email_entry = tk.Entry(form_frame, width=30)
website_entry = tk.Entry(form_frame, width=30)

company_entry.grid(row=0, column=1)
email_entry.grid(row=1, column=1)
website_entry.grid(row=2, column=1)

tk.Button(form_frame, text="Add", command=add_company).grid(row=0, column=2, rowspan=3)

# LIST
contact_list = tk.Listbox(root, width=80, height=20)
contact_list.pack(pady=10)

# ACTIONS
btn_frame = tk.Frame(root)
btn_frame.pack()

tk.Button(btn_frame, text="Start Campaign", command=start_campaign).grid(row=0, column=0)
tk.Button(btn_frame, text="Follow Up 1", command=start_followups).grid(row=0, column=1)
tk.Button(btn_frame, text="Follow Up 2", command=start_followup2).grid(row=0, column=2)
tk.Button(btn_frame, text="Final Follow Up", command=start_followup3).grid(row=0, column=3)
tk.Button(btn_frame, text="Delete", command=delete_company).grid(row=0, column=4)
tk.Button(btn_frame, text="Stats", command=show_stats).grid(row=0, column=5)

# LOAD DATA
load_contacts()

with contacts_lock:
    for c in contacts:
        contact_list.insert(
            tk.END,
            f"{c['company']} | {c['email']} | {c['status']}"
        )

# START AUTO CHECK
auto_check_replies()

root.mainloop()