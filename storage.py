import sqlite3
import os
from config import DB_PATH

def init_db():
    """Initialize the database and create table if not exists."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Table to store the latest sent link
    c.execute('''
        CREATE TABLE IF NOT EXISTS latest (
            id INTEGER PRIMARY KEY,
            link TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

def get_latest_link():
    """Return the latest link that was sent, or None if none."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT link FROM latest LIMIT 1')
    row = c.fetchone()
    conn.close()
    if row:
        return row[0]
    return None

def save_latest_link(link):
    """Save the link as the latest sent link, replacing any previous."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Delete existing rows
    c.execute('DELETE FROM latest')
    # Insert new link
    c.execute('INSERT INTO latest (link) VALUES (?)', (link,))
    conn.commit()
    conn.close()