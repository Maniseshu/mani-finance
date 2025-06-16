
import sqlite3
from flask import request, render_template, redirect, url_for, flash

def repay_personal_loan_route(app):
    @app.route('/repay-personal-loan', methods=['GET', 'POST'])
    def repay_personal_loan():
        conn = sqlite3.connect('finance_app.db')
        c = conn.cursor()

        try:
            c.execute("ALTER TABLE personal_loan ADD COLUMN repay_date TEXT")
            c.execute("ALTER TABLE personal_loan ADD COLUMN repay_amount REAL")
            c.execute("ALTER TABLE personal_loan ADD COLUMN received_interest REAL")
            c.execute("ALTER TABLE personal_loan ADD COLUMN remarks TEXT")
            conn.commit()
        except:
            pass

        search_results = []
        if request.method == 'POST' and 'search_by' in request.form:
            search_by = request.form['search_by']
            search_value = request.form['search_value']
            query = "SELECT * FROM personal_loan WHERE 1=1"
            params = []

            if search_by == 'PBill Number':
                query += " AND pbill_number = ?"
                params.append(search_value)
            elif search_by == 'Customer Name':
                query += " AND customer_name LIKE ?"
                params.append(f"%{search_value}%")
            elif search_by == 'Phone Number':
                query += " AND customer_phone LIKE ?"
                params.append(f"%{search_value}%")
            elif search_by == 'Loan Date':
                query += " AND loan_date = ?"
                params.append(search_value)
            elif search_by == 'PBill Status':
                query += " AND pbill_status = ?"
                params.append(search_value)

            c.execute(query, params)
            search_results = c.fetchall()

        conn.close()
        return render_template('repay_personal_loan.html', search_results=search_results)

    @app.route('/repay-personal-loan-view', methods=['POST'])
    def repay_personal_loan_view():
        pbill_number = request.form['pbill_number']
        conn = sqlite3.connect('finance_app.db')
        c = conn.cursor()
        c.execute("SELECT * FROM personal_loan WHERE pbill_number = ?", (pbill_number,))
        personal_loan = c.fetchone()
        conn.close()
        return render_template('repay_personal_loan.html', personal_loan=personal_loan)

    @app.route('/repay-personal-loan-update', methods=['POST'])
    def repay_personal_loan_update():
        pbill_number = request.form['pbill_number']
        repay_date = request.form['repay_date']
        repay_amount = float(request.form['repay_amount'])
        received_interest = float(request.form['received_interest'])
        remarks = request.form['remarks']
        pbill_status = request.form.get('pbill_status', 'Open')

        conn = sqlite3.connect('finance_app.db')
        c = conn.cursor()
        c.execute('''
            UPDATE personal_loan SET
                repay_date = ?, repay_amount = ?, received_interest = ?, remarks = ?, pbill_status = ?
            WHERE pbill_number = ?
        ''', (repay_date, repay_amount, received_interest, remarks, pbill_status, pbill_number))
        conn.commit()
        conn.close()
        flash("Personal loan repayment details updated successfully!", "success")
        return redirect(url_for('repay_personal_loan'))
