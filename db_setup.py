# db_setup.py
import sqlite3
from werkzeug.security import generate_password_hash

def init_db():
    conn = sqlite3.connect('finance_app.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  ('admin', generate_password_hash('admin123')))
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  ('user1', generate_password_hash('pass123')))
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('finance_app.db')
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == '__main__':
    init_db()
