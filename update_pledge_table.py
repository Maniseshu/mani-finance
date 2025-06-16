
import os
import sqlite3

# Step 1: Drop investments table from the database
def drop_investment_table():
    try:
        conn = sqlite3.connect('finance_app.db')
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS investments")
        conn.commit()
        conn.close()
        print("✅ 'investments' table dropped successfully.")
    except Exception as e:
        print(f"❌ Failed to drop table: {e}")

# Step 2: Delete investment-related files
def delete_investment_files():
    files_to_delete = [
        "screens/investment_screen.py",
        "screens/edit_investment_screen.py",
        "templates/investment.html",
        "templates/edit_investment.html"
    ]
    for file in files_to_delete:
        try:
            if os.path.exists(file):
                os.remove(file)
                print(f"✅ Deleted: {file}")
            else:
                print(f"ℹ️ File not found, skipped: {file}")
        except Exception as e:
            print(f"❌ Error deleting {file}: {e}")

if __name__ == "__main__":
    drop_investment_table()
    delete_investment_files()
