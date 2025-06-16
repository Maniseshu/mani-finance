import sqlite3
from flask import request, redirect, url_for
from datetime import datetime, timedelta

def calculate_balance_for_date(date_str):
    conn = sqlite3.connect('finance_app.db')
    c = conn.cursor()

    # Get previous day's closing balance
    prev_date = (datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    c.execute("SELECT closing_balance FROM daily_balances WHERE date = ?", (prev_date,))
    prev_closing = c.fetchone()
    prev_closing_balance = prev_closing[0] if prev_closing else 0

    opening_balance = prev_closing_balance

    # Get values
    c.execute("SELECT SUM(invested_amount) FROM investments WHERE investment_date = ?", (date_str,))
    add_investment = c.fetchone()[0] or 0

    c.execute("SELECT SUM(loan_amount), SUM(received_interest) FROM pledge WHERE bill_status = 'Release' AND release_date = ?", (date_str,))
    gold_loan_repay = c.fetchone()
    gold_repay_loan = gold_loan_repay[0] or 0
    gold_repay_interest = gold_loan_repay[1] or 0

    c.execute("SELECT SUM(repay_amount), SUM(received_interest) FROM personal_loan WHERE pbill_status = 'Close' AND repay_date = ?", (date_str,))
    personal_repay = c.fetchone()
    personal_repay_amount = personal_repay[0] or 0
    personal_repay_interest = personal_repay[1] or 0

    c.execute("SELECT SUM(loan_amount) FROM pledge WHERE pledge_date = ?", (date_str,))
    gold_loans = c.fetchone()[0] or 0

    c.execute("SELECT SUM(loan_amount) FROM personal_loan WHERE loan_date = ?", (date_str,))
    personal_loans = c.fetchone()[0] or 0

    c.execute("SELECT SUM(amount) FROM expenses WHERE expense_date = ?", (date_str,))
    expenses = c.fetchone()[0] or 0

    c.execute("SELECT SUM(repay_loan_amount), SUM(repay_interest_amount) FROM investments WHERE investment_status = 'Close' AND repay_date = ?", (date_str,))
    repay_inv = c.fetchone()
    repay_loan = repay_inv[0] or 0
    repay_interest = repay_inv[1] or 0

    total_inflow = add_investment + gold_repay_loan + gold_repay_interest + personal_repay_amount + personal_repay_interest
    total_outflow = gold_loans + personal_loans + expenses + repay_loan + repay_interest

    closing_balance = opening_balance + total_inflow - total_outflow

    c.execute("INSERT OR REPLACE INTO daily_balances (date, opening_balance, closing_balance) VALUES (?, ?, ?)",
              (date_str, opening_balance, closing_balance))
    conn.commit()
    conn.close()

def recalculate_balances_route(app):
    @app.route('/recalculate-balances-all', methods=['POST'])
    def recalc_all():
        conn = sqlite3.connect('finance_app.db')
        c = conn.cursor()
        c.execute("SELECT DISTINCT pledge_date FROM pledge")
        all_dates = sorted(set(row[0] for row in c.fetchall()))
        conn.close()

        for d in all_dates:
            calculate_balance_for_date(d)
        return redirect(url_for('daily_transactions'))

    @app.route('/recalculate-balances-range', methods=['POST'])
    def recalc_range():
        from_date = request.form['from_date']
        to_date = request.form['to_date']
        start = datetime.strptime(from_date, "%Y-%m-%d")
        end = datetime.strptime(to_date, "%Y-%m-%d")

        delta = timedelta(days=1)
        while start <= end:
            calculate_balance_for_date(start.strftime("%Y-%m-%d"))
            start += delta
        return redirect(url_for('daily_transactions'))
