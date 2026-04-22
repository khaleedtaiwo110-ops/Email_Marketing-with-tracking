from flask import Flask, request, send_file
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

DB_PATH = "project atm/campaign.db"

@app.route("/open")
def track_open():
    email = request.args.get("email")

    if email:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE contacts
            SET opened = 1, opened_at = ?
            WHERE email = ?
        """, (datetime.now(), email))

        conn.commit()
        conn.close()

    return "OK"

@app.route("/")
def home():
    return "Tracking server is running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)