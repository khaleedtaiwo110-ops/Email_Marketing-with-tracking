from flask import Flask, request, send_file, jsonify
import sqlite3
import os
import base64

app = Flask(__name__)
DB_PATH = "campaign.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS opens (
            email TEXT PRIMARY KEY,
            opened_at TEXT
        )
    """)
    conn.commit()
    conn.close()


@app.route("/open")
def track_open():
    email = request.args.get("email")
    user_agent = request.headers.get("User-Agent", "").lower()

    # 🚀 FIXED: Removed googleimageproxy so real Gmail opens are allowed through!
    bot_keywords = ["yahoo! slurp", "bingpreview", "bot", "spider", "crawler"]
    if any(keyword in user_agent for keyword in bot_keywords):
        print(f"🤖 Blocked automated crawler bot: {user_agent}")
        return send_blank_pixel()

    if email:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS opens (email TEXT PRIMARY KEY, opened_at TEXT)")

            # Record the open (normalize email to lowercase to prevent duplicates)
            cursor.execute("""
                INSERT INTO opens (email, opened_at)
                VALUES (?, datetime('now'))
                ON CONFLICT(email) DO NOTHING
            """, (email.lower().strip(),))

            conn.commit()
            conn.close()
            print(f"🔥 Successfully recorded open for: {email}")
        except Exception as e:
            print("Database Error:", e)

    return send_blank_pixel()


def send_blank_pixel():
    if os.path.exists("pixel.png"):
        return send_file("pixel.png", mimetype="image/png")
    # Clean fallback 1x1 transparent tracking image
    return base64.b64decode(b'R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'), 200, {
        'Content-Type': 'image/gif'}


@app.route("/stats")
def get_stats():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS opens (email TEXT PRIMARY KEY, opened_at TEXT)")
        cursor.execute("SELECT email FROM opens")
        opened_emails = [row[0] for row in cursor.fetchall()]
        conn.close()
        return jsonify({"opened_emails": opened_emails})
    except Exception as e:
        return jsonify({"opened_emails": [], "error": str(e)})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)