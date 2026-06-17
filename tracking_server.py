from flask import Flask, request, send_file, jsonify
import sqlite3
import os
import base64

import urllib.parse

app = Flask(__name__)
DB_PATH = "campaign.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Initialize the main opens tracking table cleanly
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS opens (
            email TEXT PRIMARY KEY,
            opened_at TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.route("/open/<path:encoded_email>")
def track_open(encoded_email):
    user_agent = request.headers.get("User-Agent", "").lower()

    # 1x1 Transparent tracking GIF pixel bytes
    blank_pixel_data = base64.b64decode(b'R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7')
    pixel_headers = {'Content-Type': 'image/gif'}

    # Block automated crawler bots
    bot_keywords = ["yahoo! slurp", "bingpreview", "bot", "spider", "crawler"]
    if any(keyword in user_agent for keyword in bot_keywords):
        return blank_pixel_data, 200, pixel_headers

    if encoded_email:
        try:
            # Safely decode the email from the path structure
            decoded_email = urllib.parse.unquote(encoded_email)
            cleaned_email = decoded_email.strip().lower()

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS opens (
                    email TEXT PRIMARY KEY,
                    opened_at TEXT
                )
            """)

            cursor.execute("""
                INSERT INTO opens (email, opened_at)
                VALUES (?, datetime('now'))
                ON CONFLICT(email) DO UPDATE SET opened_at = datetime('now')
            """, (cleaned_email,))

            conn.commit()
            conn.close()
            print(f"👀 Live Tracked Open: {cleaned_email}")
        except Exception as e:
            print("Database Error:", e)

    return blank_pixel_data, 200, pixel_headers


@app.route("/stats")
def get_stats():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 🎯 THE FIX: Force the table to exist before reading from it
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS opens (
                email TEXT PRIMARY KEY, 
                opened_at TEXT
            )
        """)

        cursor.execute("SELECT email, opened_at FROM opens ORDER BY opened_at DESC")
        rows = cursor.fetchall()
        conn.close()

        stats_list = [{"email": row[0], "opened_at": row[1]} for row in rows]
        return jsonify({"opened_emails": stats_list, "total_unique_opens": len(stats_list)})
    except Exception as e:
        return jsonify({"opened_emails": [], "error": str(e)})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)