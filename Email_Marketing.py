import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import font as tkfont
import os
import requests
import sqlite3

from campaign import run_campaign
from db import init_db, get_connection
from followups import run_followups, run_followup2, run_followup3
from reply_tracker import check_replies_and_update

# ---------------- SETTINGS & THEME COLORS ---------------- #
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "viewtriptravels.co@gmail.com")
APP_PASSWORD = os.getenv("Gmail_app", "enni yjfi wwmj cgru")

COLOR_PRIMARY = "#1A365D"  # Deep Navy
COLOR_SECONDARY = "#2B6CB0"  # Slate Blue
COLOR_ACCENT = "#DD6B20"  # Warm Amber/Orange
COLOR_SUCCESS = "#2F855A"  # Emerald Green
COLOR_DANGER = "#C53030"  # Crimson/Corporate Red for Delete Actions
COLOR_BG = "#F7FAFC"  # Soft Light Blue/Gray Background
COLOR_CARD = "#FFFFFF"  # Solid White Block Background
COLOR_TEXT = "#2D3748"  # Dark Charcoal Text

contacts = []
contacts_lock = threading.Lock()
filter_opened_only = False

init_db()


# ---------------- DATA STORAGE LOGIC ---------------- #
# Look inside Email_Marketing.py -> load_contacts()
def load_contacts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT company, email, website, first_name, status, opened FROM contacts")
    rows = cursor.fetchall()

    with contacts_lock:
        contacts.clear()
        for row in rows:
            contacts.append({
                "company": row[0],
                "email": row[1],
                "website": row[2],
                "first_name": row[3],
                "status": row[4],
                "opened": row[5]
            })
    conn.close()


def add_company():
    company = company_entry.get().strip()
    first_name = first_name_entry.get().strip()
    email = email_entry.get().strip()
    website = website_entry.get().strip()

    if not company or not email:
        messagebox.showwarning("Input Error", "Company and Email fields are required!")
        return

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO contacts (company, first_name, email, website) VALUES (?, ?, ?, ?)",
            (company, first_name if first_name else None, email, website)
        )
        conn.commit()

        company_entry.delete(0, tk.END)
        first_name_entry.delete(0, tk.END)
        email_entry.delete(0, tk.END)
        website_entry.delete(0, tk.END)

        load_contacts()
        update_contact_list_view()
        update_status_safe(f"✅ Successfully added {company}")
    except sqlite3.IntegrityError:
        messagebox.showerror("Duplicate Error", f"The email '{email}' already exists!")
    finally:
        conn.close()

# 🎯 NEW FEATURE: DELETE SELECTED LEAD FUNCTION
def delete_company(event=None):
    try:
        selected_index = contact_list.curselection()
        if not selected_index:
            messagebox.showwarning("Selection Error",
                                   "Please click on a lead from the tracking list below to delete it.")
            return

        # Extract line details to pinpoint the targeted email
        display_row = contact_list.get(selected_index[0])

        # Parse email string directly from list formatting: ' |  ✉️ email_address | '
        parts = display_row.split("|")
        if len(parts) < 2:
            return

        email = parts[1].replace("✉️", "").strip()

        # Prompt verification dialog wrapper
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to permanently remove this record from your pipeline?\n\nTarget Email: {email}"
        )

        if confirm:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM contacts WHERE email=?", (email,))
            conn.commit()
            conn.close()

            update_status_safe(f"🗑️ Removed lead: {email}")
            load_contacts()
            update_contact_list_view()
    except Exception as e:
        messagebox.showerror("System Error", f"Failed to execute row deletion: {str(e)}")


def update_contact_list_view():
    contact_list.delete(0, tk.END)
    with contacts_lock:
        for c in contacts:
            if filter_opened_only and c.get('opened') != 1:
                continue

            status_text = c.get('status', 'pending').upper()
            open_tag = "  [🔥 OPENED]" if c.get('opened') == 1 else ""

            display_row = f" 🏢 {c['company'].ljust(22)} |  ✉️ {c['email'].ljust(32)} |  📊 {status_text}{open_tag}"
            contact_list.insert(tk.END, display_row)


def update_ui_callback(index, contact, status):
    root.after(0, update_contact_list_view)


def update_status_safe(text):
    root.after(0, lambda: status_label.config(text=text))


# ---------------- BACKGROUND THREAD WORKERS ---------------- #
def start_campaign():
    load_contacts()
    threading.Thread(target=run_campaign,
                     args=(contacts, update_ui_callback, SENDER_EMAIL, APP_PASSWORD, update_status_safe),
                     daemon=True).start()


def toggle_opened_filter():
    global filter_opened_only
    filter_opened_only = not filter_opened_only

    if filter_opened_only:
        opened_btn.config(text="Show All Contacts", bg=COLOR_SUCCESS)
        update_status_safe("🔍 Filter Applied: Showing locally cached opens. Fetching live sync...")
    else:
        opened_btn.config(text="Show Opened Only", bg=COLOR_ACCENT)
        update_status_safe("📋 View Reset: Showing full pipeline contact list.")

    update_contact_list_view()

    def silent_sync_backend():
        sync_completed = show_stats(silent=True)
        if sync_completed and filter_opened_only:
            update_status_safe("🔍 Filter Applied: Live server sync complete.")
            root.after(0, update_contact_list_view)

    threading.Thread(target=silent_sync_backend, daemon=True).start()


def start_followups():
    load_contacts()
    threading.Thread(target=run_followups,
                     args=(contacts, update_ui_callback, SENDER_EMAIL, APP_PASSWORD, update_status_safe),
                     daemon=True).start()


def start_followup2():
    load_contacts()
    threading.Thread(target=run_followup2,
                     args=(contacts, update_ui_callback, SENDER_EMAIL, APP_PASSWORD, update_status_safe),
                     daemon=True).start()


def start_followup3():
    load_contacts()
    threading.Thread(target=run_followup3,
                     args=(contacts, update_ui_callback, SENDER_EMAIL, APP_PASSWORD, update_status_safe),
                     daemon=True).start()


def check_replies():
    update_status_safe("📥 Scanning IMAP mail server inbox for incoming warm replies...")
    threading.Thread(target=check_replies_and_update, args=(contacts, contact_list, SENDER_EMAIL, APP_PASSWORD),
                     daemon=True).start()


def show_stats(silent=False):
    try:
        response = requests.get("https://email-marketing-with-tracking.onrender.com/stats", timeout=10)
        if response.status_code == 200:
            cloud_data = response.json()
            opened_list = cloud_data.get("opened_emails", [])
            opened_set = {email.lower().strip() for email in opened_list}

            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("ALTER TABLE contacts ADD COLUMN opened INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                pass

            for email in opened_set:
                cursor.execute("UPDATE contacts SET opened = 1 WHERE LOWER(email) = ?", (email,))
            conn.commit()

            cursor.execute("SELECT COUNT(*) FROM contacts WHERE status != 'pending'")
            total_sent = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM contacts WHERE opened = 1")
            total_opened = cursor.fetchone()[0]
            conn.close()

            load_contacts()
            root.after(0, update_contact_list_view)

            if not silent:
                update_status_safe("📊 Metrics synced successfully from live tracker server.")
                messagebox.showinfo("Pipeline Metrics Dashboard",
                                    f"Total Emails Sent: {total_sent}\nUnique Real Opens: {total_opened}")
            return True
        else:
            if not silent: update_status_safe(f"❌ Cloud server error code: {response.status_code}")
            return False
    except Exception as e:
        if not silent: update_status_safe(f"❌ Network Sync Exception: {e}")
        return False


# ---------------- TKINTER LAYOUT ENVIRONMENT ---------------- #
root = tk.Tk()
root.title("Viewtrip Logistics CRM — Email Marketing Dashboard")
root.geometry("900x640")
root.configure(bg=COLOR_BG)

font_title = tkfont.Font(family="Segoe UI", size=11, weight="bold")
font_label = tkfont.Font(family="Segoe UI", size=10, weight="bold")
font_entry = tkfont.Font(family="Segoe UI", size=10)
font_button = tkfont.Font(family="Segoe UI", size=9, weight="bold")
font_list = tkfont.Font(family="Consolas", size=10)

# BLOCK 1: Data Acquisition Form Frame
form_frame = tk.LabelFrame(root, text=" PIPELINE LEAD MANAGEMENT ", font=font_title, bg=COLOR_CARD, fg=COLOR_PRIMARY,
                           bd=2, relief="groove", padx=15, pady=15)
form_frame.pack(fill="x", padx=20, pady=15)

# 1. Labels Layout
tk.Label(form_frame, text="Company Name:", font=font_label, bg=COLOR_CARD, fg=COLOR_TEXT).grid(row=0, column=0, sticky="w", pady=4)
# 🎯 ADD THIS LINE HERE:
tk.Label(form_frame, text="First Name (Optional):", font=font_label, bg=COLOR_CARD, fg=COLOR_TEXT).grid(row=1, column=0, sticky="w", pady=4)
tk.Label(form_frame, text="Target Email:", font=font_label, bg=COLOR_CARD, fg=COLOR_TEXT).grid(row=2, column=0, sticky="w", pady=4)
tk.Label(form_frame, text="Corporate Web URL:", font=font_label, bg=COLOR_CARD, fg=COLOR_TEXT).grid(row=3, column=0, sticky="w", pady=4)

# 2. Creating Entry Box Objects
company_entry = tk.Entry(form_frame, font=font_entry, bd=1, relief="solid", width=36)
first_name_entry = tk.Entry(form_frame, font=font_entry, bd=1, relief="solid", width=36)
email_entry = tk.Entry(form_frame, font=font_entry, bd=1, relief="solid", width=36)
website_entry = tk.Entry(form_frame, font=font_entry, bd=1, relief="solid", width=36)

# 3. Entry Box Grid Grid Placements (row numbers shifted down by 1 below)
company_entry.grid(row=0, column=1, padx=10, pady=4)
first_name_entry.grid(row=1, column=1, padx=10, pady=4)
email_entry.grid(row=2, column=1, padx=10, pady=4)
website_entry.grid(row=3, column=1, padx=10, pady=4)

# 4. Action Button Rowspan updated from 3 to 4 to stretch along with the fields
add_btn = tk.Button(form_frame, text="➕ Add Lead", command=add_company, font=font_button, bg=COLOR_PRIMARY, fg="white",
                    relief="flat", activebackground=COLOR_SECONDARY, activeforeground="white", width=12, height=2)
add_btn.grid(row=0, column=2, rowspan=4, padx=10, sticky="ns") # 👈 Changed rowspan to 4
# 🎯 ADDED ACTION CONTROL: Styled Delete Button Layout Tray
delete_btn = tk.Button(form_frame, text="🗑️ Delete Lead", command=delete_company, font=font_button, bg=COLOR_DANGER,
                       fg="white", relief="flat", activebackground="#9B2C2C", activeforeground="white", width=12,
                       height=2)
delete_btn.grid(row=0, column=3, rowspan=3, padx=5, sticky="ns")

# BLOCK 2: Data Pipeline Workspace Frame
list_frame = tk.LabelFrame(root, text=" CAMPAIGN DISTRIBUTION TRACKER ", font=font_title, bg=COLOR_CARD,
                           fg=COLOR_PRIMARY, bd=2, relief="groove", padx=15, pady=15)
list_frame.pack(fill="both", expand=True, padx=20, pady=5)

scrollbar = tk.Scrollbar(list_frame, orient="vertical")
contact_list = tk.Listbox(list_frame, width=100, height=14, font=font_list, bd=1, relief="solid", fg=COLOR_TEXT,
                          bg="#FAFAFA", selectbackground=COLOR_SECONDARY, yscrollcommand=scrollbar.set)
scrollbar.config(command=contact_list.yview)

scrollbar.pack(side="right", fill="y")
contact_list.pack(side="left", fill="both", expand=True)

# 🎯 USER CONVENIENCE: Bind the keyboard "Delete" key to instantly run the delete engine
contact_list.bind("<Delete>", delete_company)

# BLOCK 3: Functional Interactive Controls Block tray
btn_frame = tk.Frame(root, bg=COLOR_BG)
btn_frame.pack(fill="x", padx=20, pady=15)

btn_configs = [
    ("🚀 Start Campaign", start_campaign, COLOR_PRIMARY, 0),
    ("Follow Up 1", start_followups, COLOR_SECONDARY, 2),
    ("Follow Up 2", start_followup2, COLOR_SECONDARY, 3),
    ("Final Follow Up", start_followup3, COLOR_SECONDARY, 4),
    ("📥 Check Replies", check_replies, "#4A5568", 5),
    ("📊 Sync Stats", lambda: show_stats(silent=False), "#3182CE", 6)
]

for text, cmd, bg_color, col in btn_configs:
    tk.Button(btn_frame, text=text, command=cmd, font=font_button, bg=bg_color, fg="white", relief="flat",
              activebackground="#4A5568", height=2, width=13).grid(row=0, column=col, padx=4)

opened_btn = tk.Button(btn_frame, text="Show Opened Only", command=toggle_opened_filter, font=font_button,
                       bg=COLOR_ACCENT, fg="white", relief="flat", height=2, width=16)
opened_btn.grid(row=0, column=1, padx=4)

# BLOCK 4: Status Tray
status_frame = tk.Frame(root, bd=1, relief="sunken", bg="#E2E8F0")
status_frame.pack(side="bottom", fill="x")
status_label = tk.Label(status_frame, text="System Ready", font=("Segoe UI", 9), bg="#E2E8F0", fg="#4A5568", anchor="w",
                        padx=10, pady=3)
status_label.pack(fill="x")

load_contacts()
update_contact_list_view()

root.mainloop()