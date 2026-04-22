import sqlite3

DB_PATH = "project atm/campaign.db"

# ---------------- CONNECTION ---------------- #
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn

# ---------------- INIT DB ---------------- #
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contacts(
        company TEXT,
        email TEXT UNIQUE,
        website TEXT,

        status TEXT DEFAULT 'pending',

        sent_at TEXT,

        opened INTEGER DEFAULT 0,
        opened_at TEXT,

        clicked INTEGER DEFAULT 0,
        clicked_at TEXT,

        replied INTEGER DEFAULT 0,
        replied_at TEXT
    )
    """)

    conn.commit()
    conn.close()