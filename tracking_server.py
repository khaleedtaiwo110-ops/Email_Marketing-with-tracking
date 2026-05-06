from flask import Flask, request, send_file, jsonify
import sqlite3
import os
from flask import redirect
from datetime import datetime


app = Flask(__name__)

DB_PATH = "campaign.db"

@app.route("/open")
def track_open():
    email = request.args.get("email")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                email TEXT PRIMARY KEY,
                opened INTEGER DEFAULT 0,
                opened_at TEXT
            )
        """)

        if email:
            cursor.execute("""
                INSERT INTO contacts (email, opened, opened_at)
                VALUES (?, 1, datetime('now'))
                ON CONFLICT(email) DO UPDATE SET
                opened=1,
                opened_at=datetime('now')
            """, (email,))

        conn.commit()
        conn.close()

    except Exception as e:
        print("ERROR:", e)

    return "OK"

@app.route("/")
def home():
    return "Tracking server is running"

@app.route("/click")
def track_click():
    email = request.args.get("email")
    url = request.args.get("url")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            ALTER TABLE contacts ADD COLUMN clicked INTEGER DEFAULT 0
        """)
    except:
        pass

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE contacts
            SET clicked = 1
            WHERE email = ?
        """, (email,))

        conn.commit()
        conn.close()

    except Exception as e:
        print("ERROR:", e)

    return redirect(url)

@app.route("/stats")
def get_stats():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM contacts")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM contacts WHERE opened=1")
        opened = cursor.fetchone()[0]

        conn.close()

        return jsonify({
            "total": total,
            "opened": opened
        })

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)