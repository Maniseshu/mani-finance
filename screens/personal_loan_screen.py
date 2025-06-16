# screens/personal_loan_screen.py
import sqlite3
from flask import request, render_template, redirect, url_for, flash
from datetime import datetime

def personal_loan_route(app):
    @app.route('/personal-loan', methods=['GET', 'POST'])
    def personal_loan():
        if 'username' not in request.cookies and 'username' not in app.session_interface.open_session(app, request):
            return redirect(url_for('login'))

        conn = sqlite3.connect('finance_app.db')
        c = conn.cursor()

        # Ensure table exists before working with it
        c.execute('''CREATE TABLE IF NOT EXISTS personal_loan (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        customer_name TEXT,
                        customer_phone TEXT,
                        loan_amount REAL,
                        interest_rate REAL,
                        loan_date TEXT,
                        pbill_number TEXT,
                        pbill_status TEXT
                    )''')
        conn.commit()

        # Get the latest PB number
        c.execute("SELECT pbill_number FROM personal_loan ORDER BY id DESC LIMIT 1")
        last_bill = c.fetchone()

        if last_bill and last_bill[0].startswith("PB-"):
            try:
                last_number = int(last_bill[0].split("-")[1])
                next_pbill_number = f"PB-{last_number + 1}"
            except ValueError:
                next_pbill_number = "PB-1"
        else:
            next_pbill_number = "PB-1"

        if request.method == 'POST':
            customer_name = request.form['customer_name']
            customer_phone = request.form['customer_phone']
            loan_amount = request.form['loan_amount']
            interest_rate = request.form['interest_rate']
            loan_date = request.form['loan_date']
            pbill_number = request.form['pbill_number']  # use the generated one
            pbill_status = request.form['pbill_status']

            c.execute('''INSERT INTO personal_loan (
                            customer_name, customer_phone, loan_amount,
                            interest_rate, loan_date, pbill_number, pbill_status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (customer_name, customer_phone, loan_amount,
                       interest_rate, loan_date, pbill_number, pbill_status))
            conn.commit()
            conn.close()

            flash('Personal loan submitted successfully!', 'success')
            return redirect(url_for('personal_loan'))

        conn.close()
        return render_template(
            'personal_loan.html',
            today=datetime.today().strftime('%Y-%m-%d'),
            next_pbill_number=next_pbill_number
        )
