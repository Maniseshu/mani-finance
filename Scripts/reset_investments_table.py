import sqlite3

conn = sqlite3.connect('finance_app.db')
c = conn.cursor()

# Drop existing (corrupted or partial) table
c.execute("DROP TABLE IF EXISTS investments")

# Create new investments table with full structure
c.execute('''
    CREATE TABLE investments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        investment_transaction_id TEXT,
        investment_date TEXT,
        investment_source TEXT,
        invested_amount REAL,
        interest_rate REAL,
        loan_from TEXT,
        investment_by TEXT,
        investment_status TEXT,
        investment_remarks TEXT,
        repay_date TEXT,
        repay_loan_amount REAL,
        repay_interest_amount REAL
    )
''')

conn.commit()
conn.close()

print("✅ Fresh investments table created with all required columns.")
