
import sqlite3
from flask import request, render_template, redirect, url_for, flash
from datetime import datetime

def repay_investment_route(app):
    @app.route('/repay-investment', methods=['GET', 'POST'])
    def repay_investment():
        conn = sqlite3.connect('finance_app.db')
        c = conn.cursor()

        search_results = []
        if request.method == 'POST' and 'search_by' in request.form:
            search_by = request.form['search_by']
            search_value = request.form['search_value']
            query = "SELECT * FROM investments WHERE 1=1"
            params = []
            if search_by == 'Investment Transaction ID':
                query += " AND investment_transaction_id = ?"
                params.append(search_value)
            elif search_by == 'Date of Investment':
                query += " AND investment_date = ?"
                params.append(search_value)
            elif search_by == 'Loan From':
                query += " AND loan_from LIKE ?"
                params.append(f"%{search_value}%")
            elif search_by == 'Investment By':
                query += " AND investment_by LIKE ?"
                params.append(f"%{search_value}%")
            elif search_by == 'Investment Status':
                query += " AND investment_status = ?"
                params.append(search_value)
            c.execute(query, params)
            search_results = c.fetchall()
            conn.close()
            return render_template('repay_investment_view_edit.html', search_results=search_results, today=datetime.today().strftime('%Y-%m-%d'))

        conn.close()
        return render_template('repay_investment_view_edit.html', search_results=[], today=datetime.today().strftime('%Y-%m-%d'))

    @app.route('/repay-investment-view', methods=['POST'])
    def repay_investment_view():
        transaction_id = request.form['transaction_id']
        conn = sqlite3.connect('finance_app.db')
        c = conn.cursor()
        c.execute("SELECT * FROM investments WHERE investment_transaction_id = ?", (transaction_id,))
        investment = c.fetchone()
        conn.close()

        if investment:
            try:
                inv_date = investment[2]
                formatted_investment_date = datetime.strptime(inv_date, "%Y-%m-%d").strftime("%Y-%m-%d")
            except Exception:
                formatted_investment_date = investment[2]

            return render_template(
                'repay_investment_view_edit.html',
                search_results=[],
                investment=investment,
                today=datetime.today().strftime('%Y-%m-%d'),
                investment_date_formatted=formatted_investment_date
            )
        else:
            flash("Investment not found!", "danger")
            return redirect(url_for('repay_investment'))

    @app.route('/repay-investment-update', methods=['POST'])
    def repay_investment_update():
        data = request.form
        conn = sqlite3.connect('finance_app.db')
        c = conn.cursor()
        c.execute('''
            UPDATE investments SET
                investment_date = ?, investment_source = ?, invested_amount = ?, interest_rate = ?, loan_from = ?,
                investment_by = ?, investment_status = ?, repay_date = ?, repay_loan_amount = ?, repay_interest_amount = ?
            WHERE investment_transaction_id = ?
        ''', (
            data['investment_date'], data['investment_source'], data['invested_amount'], data['interest_rate'],
            data['loan_from'], data['investment_by'], data['investment_status'], data['repay_date'],
            data['repay_loan_amount'], data['repay_interest_amount'], data['transaction_id']
        ))
        conn.commit()
        conn.close()
        flash("Investment updated successfully!", "success")
        return redirect(url_for('repay_investment'))
