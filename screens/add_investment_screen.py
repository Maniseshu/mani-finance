import sqlite3
from flask import request, render_template, redirect, url_for, flash
from datetime import datetime

def add_investment_route(app):
    @app.route('/add-investment', methods=['GET', 'POST'])
    def add_investment():
        if 'username' not in request.cookies and 'username' not in app.session_interface.open_session(app, request):
            return redirect(url_for('login'))

        # Connect to DB
        conn = sqlite3.connect('finance_app.db')
        c = conn.cursor()

        # Create the investments table if not exists
        c.execute('''
            CREATE TABLE IF NOT EXISTS investments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                investment_transaction_id TEXT,
                investment_date TEXT,
                investment_source TEXT,
                invested_amount REAL,
                interest_rate REAL,
                loan_from TEXT,
                investment_by TEXT,
                investment_status TEXT,
                investment_remarks TEXT
            )
        ''')
        conn.commit()

        # On form submit
        if request.method == 'POST':
            transaction_id = request.form['investment_transaction_id']
            investment_date = request.form['investment_date']
            investment_source = request.form['investment_source']
            invested_amount = float(request.form['invested_amount'])
            interest_rate = float(request.form['interest_rate'])
            loan_from = request.form['loan_from']
            investment_by = request.form['investment_by']
            investment_status = request.form['investment_status']
            investment_remarks = request.form['investment_remarks']

            # Insert into DB
            c.execute('''
                INSERT INTO investments (
                    investment_transaction_id, investment_date, investment_source,
                    invested_amount, interest_rate, loan_from, investment_by,
                    investment_status, investment_remarks
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                transaction_id, investment_date, investment_source,
                invested_amount, interest_rate, loan_from, investment_by,
                investment_status, investment_remarks
            ))
            conn.commit()
            conn.close()

            flash('Investment added successfully!', 'success')
            return redirect(url_for('add_investment'))

        # On initial load, generate next transaction ID
        c.execute("SELECT investment_transaction_id FROM investments ORDER BY id DESC LIMIT 1")
        last = c.fetchone()
        if last:
            last_id = int(last[0].split('-')[1])
            next_id = f"ITID-{last_id + 1:04d}"
        else:
            next_id = "ITID-0001"

        conn.close()
        return render_template(
            'add_investment.html',
            transaction_id=next_id,
            today=datetime.today().strftime('%Y-%m-%d')
        )
