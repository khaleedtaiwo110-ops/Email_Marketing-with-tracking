import sqlite3

DB_PATH = "campaign.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Added UNIQUE constraint to email column
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        first_name TEXT,
        email TEXT UNIQUE,
        website TEXT,
        status TEXT DEFAULT 'pending',
        sent_at TEXT,
        opened INTEGER DEFAULT 0,
        clicked INTEGER DEFAULT 0,
        replied INTEGER DEFAULT 0,
        replied_at TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()
    # israel.aye@oneworq.com