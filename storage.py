import sqlite3
import hashlib
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  link TEXT NOT NULL,
                  pub_date TEXT,
                  score INTEGER,
                  summary TEXT,
                  UNIQUE(title, link))''')
    conn.commit()
    conn.close()

def _hash_item(title, link):
    return hashlib.md5((title + link).encode('utf-8')).hexdigest()

def is_seen(title, link):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM items WHERE title=? AND link=?", (title, link))
    row = c.fetchone()
    conn.close()
    return row is not None

def save_item(title, link, pub_date, score, summary):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("""INSERT INTO items (title, link, pub_date, score, summary)
                     VALUES (?, ?, ?, ?, ?)""",
                  (title, link, pub_date, score, summary))
        conn.commit()
        inserted = True
    except sqlite3.IntegrityError:
        inserted = False
    conn.close()
    return inserted