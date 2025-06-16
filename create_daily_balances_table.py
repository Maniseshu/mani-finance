import sqlite3

def create_daily_balances_table():
    conn = sqlite3.connect('finance_app.db')
    c = conn.cursor()

    # Create the daily_balances table if not exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_balances (
            date TEXT PRIMARY KEY,
            opening_balance REAL,
            closing_balance REAL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ daily_balances table created (if not exists).")

if __name__ == '__main__':
    create_daily_balances_table()
