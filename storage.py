import sqlite3
import os
from config import DB_PATH

def init_db():
    """Initialize the database and create table for tracking last article per section."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS section_last (
            section_url TEXT PRIMARY KEY,
            last_title TEXT,
            last_link TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_last(section_url):
    """Return (last_title, last_link) for the given section, or None if not found."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT last_title, last_link FROM section_last WHERE section_url = ?', (section_url,))
    row = c.fetchone()
    conn.close()
    if row:
        return (row[0], row[1])
    return None

def update_last(section_url, title, link):
    """Update or insert the last seen title and link for the section."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO section_last (section_url, last_title, last_link)
        VALUES (?, ?, ?)
        ON CONFLICT(section_url) DO UPDATE SET
            last_title = excluded.last_title,
            last_link = excluded.last_link
    ''', (section_url, title, link))
    conn.commit()
    conn.close()