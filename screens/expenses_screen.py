
import sqlite3
from flask import request, render_template, redirect, url_for, flash, session
from datetime import datetime

def expenses_route(app):
    @app.route('/expenses', methods=['GET', 'POST'])
    def expenses():
        if 'username' not in session:
            return redirect(url_for('login'))

        conn = sqlite3.connect('finance_app.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS expenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        expense_type TEXT,
                        amount REAL,
                        expense_date TEXT,
                        remarks TEXT
                    )''')

        if request.method == 'POST':
            expense_type = request.form['expense_type']
            amount = request.form['amount']
            expense_date = request.form['expense_date']
            remarks = request.form['remarks']

            c.execute('INSERT INTO expenses (expense_type, amount, expense_date, remarks) VALUES (?, ?, ?, ?)',
                      (expense_type, amount, expense_date, remarks))
            conn.commit()
            flash('Expense added successfully!', 'success')
            return redirect(url_for('expenses'))

        c.execute('SELECT * FROM expenses ORDER BY expense_date DESC')
        expenses = c.fetchall()
        conn.close()

        return render_template('expenses.html', expenses=expenses, today=datetime.today().strftime('%Y-%m-%d'))

    @app.route('/edit-expense/<int:expense_id>', methods=['GET', 'POST'])
    def edit_expense(expense_id):
        if 'username' not in session:
            return redirect(url_for('login'))

        conn = sqlite3.connect('finance_app.db')
        c = conn.cursor()

        if request.method == 'POST':
            expense_type = request.form['expense_type']
            amount = request.form['amount']
            expense_date = request.form['expense_date']
            remarks = request.form['remarks']

            c.execute('UPDATE expenses SET expense_type = ?, amount = ?, expense_date = ?, remarks = ? WHERE id = ?',
                      (expense_type, amount, expense_date, remarks, expense_id))
            conn.commit()
            conn.close()
            flash('Expense updated successfully!', 'success')
            return redirect(url_for('expenses'))

        c.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,))
        expense = c.fetchone()
        conn.close()

        return render_template('edit_expense.html', expense=expense)
