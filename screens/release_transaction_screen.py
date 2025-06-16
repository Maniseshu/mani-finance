
import sqlite3
from flask import request, render_template, redirect, url_for, flash, session
from datetime import datetime

def release_transaction_route(app):
    @app.route('/release-transaction', methods=['GET', 'POST'])
    def release_transaction():
        pledge_data = None
        matching_bills = []

        if 'username' not in session:
            return redirect(url_for('login'))

        if request.method == 'POST':
            action = request.form.get('action')
            print(f"Action: {action}")  # Debug

            if action == 'search':
                keyword = request.form['search_value']
                print(f"Searching for: {keyword}")
                conn = sqlite3.connect('finance_app.db')
                c = conn.cursor()
                c.execute("SELECT * FROM pledge WHERE bill_number = ?", (keyword,))
                pledge_data = c.fetchone()

                if not pledge_data:
                    c.execute("SELECT bill_number FROM pledge WHERE customer_phone = ?", (keyword,))
                    matching_bills = c.fetchall()
                conn.close()

            elif action == 'load_bill':
                selected_bill = request.form['selected_bill']
                print(f"Loading bill: {selected_bill}")
                conn = sqlite3.connect('finance_app.db')
                c = conn.cursor()
                c.execute("SELECT * FROM pledge WHERE bill_number = ?", (selected_bill,))
                pledge_data = c.fetchone()
                conn.close()

            elif action == 'submit':
                try:
                    # All form values
                    pledge_id = request.form['pledge_id']
                    customer_name = request.form['customer_name']
                    customer_phone = request.form['customer_phone']
                    ornament_name = request.form['ornament_name']
                    gross_weight = request.form['gross_weight']
                    net_weight = request.form['net_weight']
                    loan_amount = request.form['loan_amount']
                    interest_rate = request.form['interest_rate']
                    pledge_date = request.form['pledge_date']
                    release_date = request.form['release_date']
                    auction_date = request.form['auction_date']
                    collected_interest = request.form['collected_interest']
                    bill_status = request.form['bill_status']
                    release_remarks = request.form['release_remarks']
                    bill_remarks = request.form['bill_remarks']

                    print(f"Updating pledge_id: {pledge_id}, name: {customer_name}, phone: {customer_phone}")

                    conn = sqlite3.connect('finance_app.db')
                    c = conn.cursor()
                    c.execute("""
                        UPDATE pledge SET
                            customer_name = ?,
                            customer_phone = ?,
                            ornament_name = ?,
                            gross_weight = ?,
                            net_weight = ?,
                            loan_amount = ?,
                            interest_rate = ?,
                            pledge_date = ?,
                            release_date = ?,
                            date_of_auction_loan = ?,
                            received_interest = ?,
                            bill_status = ?,
                            pledge_remarks = ?,
                            bill_remarks = ?
                        WHERE id = ?
                    """, (
                        customer_name,
                        customer_phone,
                        ornament_name,
                        gross_weight,
                        net_weight,
                        loan_amount,
                        interest_rate,
                        pledge_date,
                        release_date,
                        auction_date,
                        collected_interest,
                        bill_status,
                        release_remarks,
                        bill_remarks,
                        pledge_id
                    ))

                    conn.commit()
                    conn.close()
                    flash('All details updated successfully!', 'success')
                    return redirect(url_for('release_transaction'))

                except Exception as e:
                    print("Error during submit:", e)
                    flash(f"Error while updating: {e}", 'danger')

        return render_template(
            'release_transaction.html',
            pledge=pledge_data,
            bills=matching_bills,
            today=datetime.today().strftime('%Y-%m-%d')
        )
