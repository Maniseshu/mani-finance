
import sqlite3
from flask import request, render_template
from datetime import datetime, timedelta

def daily_transactions_route(app):
    @app.route('/daily-transactions', methods=['GET', 'POST'])
    def daily_transactions():
        results = {}
        selected_date = ''
        opening_balance = 0
        closing_balance = 0

        if request.method == 'POST':
            selected_date = request.form['selected_date']
            conn = sqlite3.connect('finance_app.db')
            c = conn.cursor()

            prev_date = (datetime.strptime(selected_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
            c.execute("SELECT closing_balance FROM daily_balances WHERE balance_date = ?", (prev_date,))
            row = c.fetchone()
            opening_balance = row[0] if row else 0

            c.execute("SELECT SUM(invested_amount) FROM investments WHERE investment_date = ?", (selected_date,))
            invested_amount = c.fetchone()[0] or 0

            c.execute("SELECT SUM(loan_amount), SUM(received_interest) FROM pledge WHERE bill_status = 'Release' AND release_date = ?", (selected_date,))
            gold_repay = c.fetchone()
            gold_repay_loan = gold_repay[0] or 0
            gold_repay_interest = gold_repay[1] or 0

            c.execute("SELECT SUM(repay_amount), SUM(received_interest) FROM personal_loan WHERE pbill_status = 'Close' AND repay_date = ?", (selected_date,))
            personal_repay = c.fetchone()
            personal_repay_amt = personal_repay[0] or 0
            personal_interest = personal_repay[1] or 0

            c.execute("SELECT SUM(loan_amount) FROM pledge WHERE pledge_date = ?", (selected_date,))
            new_gold_loans = c.fetchone()[0] or 0

            c.execute("SELECT SUM(loan_amount) FROM personal_loan WHERE loan_date = ?", (selected_date,))
            new_personal_loans = c.fetchone()[0] or 0

            c.execute("SELECT SUM(amount) FROM expenses WHERE expense_date = ?", (selected_date,))
            expenses = c.fetchone()[0] or 0

            c.execute("SELECT SUM(repay_loan_amount), SUM(repay_interest_amount) FROM investments WHERE investment_status = 'Close' AND repay_date = ?", (selected_date,))
            repay_data = c.fetchone()
            repay_loan = repay_data[0] or 0
            repay_interest = repay_data[1] or 0

            inflow = opening_balance + invested_amount + gold_repay_loan + gold_repay_interest + personal_repay_amt + personal_interest
            outflow = new_gold_loans + new_personal_loans + expenses + repay_loan + repay_interest
            closing_balance = inflow - outflow

            c.execute("INSERT OR REPLACE INTO daily_balances (balance_date, opening_balance, closing_balance) VALUES (?, ?, ?)",
                      (selected_date, opening_balance, closing_balance))
            conn.commit()

            # Transaction details
            results['Gold Loan Transactions'] = {'headers': ['Bill Number', 'Ornament Name', 'Loan Amount'], 'data': c.execute("SELECT bill_number, ornament_name, loan_amount FROM pledge WHERE pledge_date = ?", (selected_date,)).fetchall()}
            results['Gold Loan Repays Transactions'] = {'headers': ['Bill Number', 'Loan Amount', 'Collected Interest'], 'data': c.execute("SELECT bill_number, loan_amount, received_interest FROM pledge WHERE bill_status = 'Release' AND release_date = ?", (selected_date,)).fetchall()}
            results['Personal Loan Transactions'] = {'headers': ['PBill Number', 'Loan Amount'], 'data': c.execute("SELECT pbill_number, loan_amount FROM personal_loan WHERE loan_date = ?", (selected_date,)).fetchall()}
            results['Personal Loan Repay Transactions'] = {'headers': ['PBill Number', 'P-Loan Repay Amount', 'P-Loan Received Interest'], 'data': c.execute("SELECT pbill_number, repay_amount, received_interest FROM personal_loan WHERE pbill_status = 'Close' AND repay_date = ?", (selected_date,)).fetchall()}
            results['Expenses Transactions'] = {'headers': ['Expense Type', 'Amount'], 'data': c.execute("SELECT expense_type, amount FROM expenses WHERE expense_date = ?", (selected_date,)).fetchall()}
            results['Add Investment'] = {'headers': ['Investment Transaction ID', 'Invested Amount', 'Investment By', 'Loan From'], 'data': c.execute("SELECT investment_transaction_id, invested_amount, investment_by, loan_from FROM investments WHERE investment_date = ?", (selected_date,)).fetchall()}
            results['Repay Investments'] = {'headers': ['Investment Transaction ID', 'Repay Loan Amount', 'Repay Interest Amount'], 'data': c.execute("SELECT investment_transaction_id, repay_loan_amount, repay_interest_amount FROM investments WHERE investment_status = 'Close' AND repay_date = ?", (selected_date,)).fetchall()}

            conn.close()

        return render_template('daily_transactions.html', results=results, selected_date=selected_date,
                               opening_balance=opening_balance, closing_balance=closing_balance)

    @app.route('/recalculate-daily-balances', methods=['POST'])
    def recalc_balances_range():
        from_date = request.form['from_date']
        to_date = request.form['to_date']
        current = datetime.strptime(from_date, "%Y-%m-%d")
        end = datetime.strptime(to_date, "%Y-%m-%d")

        while current <= end:
            request.form = {'selected_date': current.strftime("%Y-%m-%d")}
            daily_transactions()
            current += timedelta(days=1)
        return "Recalculated balances from {} to {}".format(from_date, to_date)

    @app.route('/recalculate-daily-balances-all', methods=['POST'])
    def recalc_balances_all():
        conn = sqlite3.connect('finance_app.db')
        c = conn.cursor()
        c.execute("SELECT DISTINCT pledge_date FROM pledge ORDER BY pledge_date")
        dates = sorted(set([row[0] for row in c.fetchall()]))
        conn.close()

        for dt in dates:
            request.form = {'selected_date': dt}
            daily_transactions()
        return "Recalculated balances for all available dates."
