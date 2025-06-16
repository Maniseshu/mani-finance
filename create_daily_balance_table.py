import sqlite3

conn = sqlite3.connect('finance_app.db')
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS daily_balances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    balance_date TEXT NOT NULL UNIQUE,
    opening_balance REAL DEFAULT 0,
    closing_balance REAL DEFAULT 0,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()