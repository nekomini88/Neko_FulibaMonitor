import sqlite3
import os
from config import DB_PATH

def init_db():
    """Initialize the database and create table for seen links."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Table to store links we have already sent
    c.execute('''
        CREATE TABLE IF NOT EXISTS seen_links (
            link TEXT PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()

def is_seen(link):
    """Return True if link has been seen before."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT 1 FROM seen_links WHERE link = ?', (link,))
    row = c.fetchone()
    conn.close()
    return row is not None

def mark_seen(link):
    """Mark the link as seen."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO seen_links (link) VALUES (?)', (link,))
        conn.commit()
    except sqlite3.IntegrityError:
        # Already exists, ignore
        pass
    finally:
        conn.close()