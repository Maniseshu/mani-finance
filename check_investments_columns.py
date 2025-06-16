import sqlite3

conn = sqlite3.connect('finance_app.db')
c = conn.cursor()

c.execute("PRAGMA table_info(investments)")
columns = c.fetchall()

print("🔍 Current 'investments' table columns:")
for col in columns:
    print(f"- {col[1]} ({col[2]})")

conn.close()