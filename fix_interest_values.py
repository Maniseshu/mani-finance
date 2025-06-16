import sqlite3

conn = sqlite3.connect('finance_app.db')
cur = conn.cursor()

# Set default interest_rate to 12% for Gold Loans where interest is NULL or 0
cur.execute("UPDATE pledge SET interest_rate = 12 WHERE interest_rate IS NULL OR interest_rate = 0")

# Set default interest_rate to 15% for Personal Loans where interest is NULL or 0
cur.execute("UPDATE personal_loan SET interest_rate = 15 WHERE interest_rate IS NULL OR interest_rate = 0")

# Set default interest_rate to 10% for Investments where interest is NULL or 0
cur.execute("UPDATE investments SET interest_rate = 10 WHERE interest_rate IS NULL OR interest_rate = 0")

conn.commit()
conn.close()

print("Interest rate defaults applied.")
