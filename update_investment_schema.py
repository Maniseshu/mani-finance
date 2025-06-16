
import sqlite3

def update_investment_schema():
    conn = sqlite3.connect('finance_app.db')
    c = conn.cursor()

    try:
        c.execute("ALTER TABLE investments ADD COLUMN total_interest_paid REAL DEFAULT 0")
    except sqlite3.OperationalError:
        print("Column total_interest_paid already exists.")

    try:
        c.execute("ALTER TABLE investments ADD COLUMN last_interest_paid_date TEXT")
    except sqlite3.OperationalError:
        print("Column last_interest_paid_date already exists.")

    try:
        c.execute("ALTER TABLE investments ADD COLUMN status TEXT DEFAULT 'Open'")
    except sqlite3.OperationalError:
        print("Column status already exists.")

    conn.commit()
    conn.close()
    print("Database updated successfully.")

if __name__ == "__main__":
    update_investment_schema()
