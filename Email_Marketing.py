import threading
import tkinter as tk
from tkinter import messagebox
import os
import requests
import sqlite3

from campaign import run_campaign
from db import init_db, get_connection
from followups import run_followups, run_followup2, run_followup3
from reply_tracker import check_replies_and_update

# ---------------- SETTINGS ---------------- #
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "viewtriptravels.co@gmail.com")
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
        messagebox.showwarning("Input Error", "Company and Email are required!")
        return

    conn = get_connection()
    cursor = conn.cursor()
    try:
        # DB Unique validation will throw IntegrityError if duplicate email exists
        cursor.execute(
            "INSERT INTO contacts (company, email, website) VALUES (?, ?, ?)",
            (company, email, website)
        )
        conn.commit()

        # Clear fields
        company_entry.delete(0, tk.END)
        email_entry.delete(0, tk.END)
        website_entry.delete(0, tk.END)

        load_contacts()
        update_contact_list_view()
        messagebox.showinfo("Success", f"Added {company} successfully!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Duplicate Error", f"The email '{email}' has already been added before!")
    finally:
        conn.close()


def update_contact_list_view():
    contact_list.delete(0, tk.END)
    with contacts_lock:
        for c in contacts:
            status_text = c.get('status', 'pending').upper()
            contact_list.insert(tk.END, f"{c['company']} | {c['email']} | {status_text}")


# ---------------- UI CALLBACK UPDATE ---------------- #
def update_ui_callback(index, contact, status):
    def safe_update():
        update_contact_list_view()

    root.after(0, safe_update)


# ---------------- BUTTON ACTIONS ---------------- #
def start_campaign():
    load_contacts()
    threading.Thread(target=run_campaign, args=(contacts, update_ui_callback, SENDER_EMAIL, APP_PASSWORD),
                     daemon=True).start()


def start_followups():
    load_contacts()
    threading.Thread(target=run_followups, args=(contacts, update_ui_callback, SENDER_EMAIL, APP_PASSWORD),
                     daemon=True).start()


def start_followup2():
    load_contacts()
    threading.Thread(target=run_followup2, args=(contacts, update_ui_callback, SENDER_EMAIL, APP_PASSWORD),
                     daemon=True).start()


def start_followup3():
    load_contacts()
    threading.Thread(target=run_followup3, args=(contacts, update_ui_callback, SENDER_EMAIL, APP_PASSWORD),
                     daemon=True).start()


def check_replies():
    threading.Thread(target=check_replies_and_update, args=(contacts, contact_list, SENDER_EMAIL, APP_PASSWORD),
                     daemon=True).start()


# ---------------- FIXED TRACKING STATS CODE ---------------- #
def show_stats():
    def fetch_stats_worker():
        try:
            root.title("📊 Syncing opens with Render cloud server...")

            # Fetch the verified JSON array from your tracking server
            response = requests.get("https://email-marketing-with-tracking.onrender.com/stats", timeout=30)

            if response.status_code == 200:
                cloud_data = response.json()
                opened_list = cloud_data.get("opened_emails", [])
                opened_set = {email.lower().strip() for email in opened_list}

                # Sync opens to your actual local DB
                conn = get_connection()
                cursor = conn.cursor()
                for email in opened_set:
                    cursor.execute("UPDATE contacts SET opened = 1 WHERE LOWER(email) = ?", (email,))
                conn.commit()

                # Calculate metrics from the updated local database
                cursor.execute("SELECT COUNT(*) FROM contacts WHERE status != 'pending'")
                total_sent = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM contacts WHERE opened = 1")
                total_opened = cursor.fetchone()[0]
                conn.close()

                # Refresh local interface windows
                load_contacts()
                root.after(0, update_contact_list_view)

                messagebox.showinfo(
                    "Verified Metrics Dashboard",
                    f"Total Emails Sent: {total_sent}\n"
                    f"Unique Real Opens: {total_opened}"
                )
            else:
                messagebox.showerror("Sync Failure", f"Server dropped code: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Network Sync Failure", f"Could not sync data pipeline:\n{e}")
        finally:
            root.title("Email Marketing System")

    threading.Thread(target=fetch_stats_worker, daemon=True).start()


# ---------------- TKINTER LAYOUT ---------------- #
root = tk.Tk()
root.title("Email Marketing System")
root.geometry("600x500")

form_frame = tk.Frame(root)
form_frame.pack(pady=10)

tk.Label(form_frame, text="Company").grid(row=0, column=0)
tk.Label(form_frame, text="Email").grid(row=1, column=0)
tk.Label(form_frame, text="Website").grid(row=2, column=0)

company_entry = tk.Entry(form_frame, width=30)
email_entry = tk.Entry(form_frame, width=30)
website_entry = tk.Entry(form_frame, width=30)

company_entry.grid(row=0, column=1)
email_entry.grid(row=1, column=1)
website_entry.grid(row=2, column=1)

tk.Button(form_frame, text="Add", command=add_company, width=10).grid(row=0, column=2, rowspan=3, padx=10)

contact_list = tk.Listbox(root, width=80, height=15)
contact_list.pack(pady=10)

btn_frame = tk.Frame(root)
btn_frame.pack()

tk.Button(btn_frame, text="Start Campaign", command=start_campaign).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Follow Up 1", command=start_followups).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Follow Up 2", command=start_followup2).grid(row=0, column=2, padx=5)
tk.Button(btn_frame, text="Final Follow Up", command=start_followup3).grid(row=0, column=3, padx=5)
tk.Button(btn_frame, text="Check Replies", command=check_replies).grid(row=0, column=4, padx=5)
tk.Button(btn_frame, text="Stats", command=show_stats, bg="lightblue").grid(row=0, column=5, padx=5)

load_contacts()
update_contact_list_view()

root.mainloop()