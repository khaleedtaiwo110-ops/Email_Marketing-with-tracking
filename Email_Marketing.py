import threading
import tkinter as tk
from tkinter import messagebox
import os

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
def show_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM contacts")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM contacts WHERE status='sent'")
    sent = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM contacts WHERE status='failed'")
    failed = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM contacts WHERE replied=1")
    replied = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM contacts WHERE opened=1")
    opened = cursor.fetchone()[0]

    conn.close()

    # Avoid division by zero
    open_rate = (opened / sent * 100) if sent else 0
    reply_rate = (replied / sent * 100) if sent else 0

    messagebox.showinfo(
        "Stats",
        f"""Total: {total}
Sent: {sent}
Failed: {failed}

Opened: {opened} ({open_rate:.1f}%)
Replied: {replied} ({reply_rate:.1f}%)"""
    )

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