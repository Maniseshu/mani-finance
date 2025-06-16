import sqlite3

conn = sqlite3.connect("finance_app.db")
c = conn.cursor()

# Add 'source' column to 'investments' table if it doesn't exist
try:
    c.execute("ALTER TABLE investments ADD COLUMN source TEXT")
    print("Column 'source' added successfully.")
except sqlite3.OperationalError as e:
    print(f"Skipping: {e}")

conn.commit()
conn.close()
