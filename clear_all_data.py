import sqlite3

def clear_all_data():
    conn = sqlite3.connect('finance_app.db')  # Adjust path if needed
    c = conn.cursor()

    tables = ['pledge', 'personal_loan', 'expenses', 'investments', 'daily_balances']
    c.execute("PRAGMA foreign_keys = OFF;")  # Temporarily disable FK checks

    for table in tables:
        try:
            c.execute(f"DELETE FROM {table};")
            print(f"Cleared data from: {table}")
        except sqlite3.OperationalError as e:
            print(f"Skipping table '{table}' - {e}")

    conn.commit()
    conn.close()
    print("✅ All existing data has been cleared where applicable.")

if __name__ == "__main__":
    clear_all_data()
