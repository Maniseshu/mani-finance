import sqlite3
from flask import request, render_template, redirect
from datetime import datetime


def investment_stats_route(app):
    @app.route('/investment-stats', methods=['GET', 'POST'])
    def investment_stats():
        results = []
        criteria = {}
        summary = {
            'total_invested': 0,
            'total_interest': 0,
            'total_repay_loan': 0,
            'total_repay_interest': 0
        }

        if request.method == 'POST':
            filters = {
                'source': request.form.get('source'),
                'status': request.form.get('status'),
                'transaction_id': request.form.get('transaction_id'),
                'investment_by': request.form.get('investment_by'),
                'start_date': request.form.get('start_date'),
                'end_date': request.form.get('end_date')
            }

            # ------------------------------------------------------------------
            #  FIX: correct column name is investment_source; alias it as source
            # ------------------------------------------------------------------
            query = (
                "SELECT investment_transaction_id, invested_amount, "
                "       investment_source AS source, loan_from, investment_by, "
                "       interest_rate, investment_status, investment_date, "
                "       repay_date, repay_loan_amount, repay_interest_amount "
                "FROM   investments "
                "WHERE  1=1"
            )
            params = []

            # --------- filters -------------------------------------------------
            if filters['source']:
                query += " AND investment_source = ?"      # ← FIX
                params.append(filters['source'])
                criteria['Source'] = filters['source']

            if filters['status'] and filters['status'] != 'All':
                query += " AND investment_status = ?"
                params.append(filters['status'])
                criteria['Status'] = filters['status']

            if filters['transaction_id']:
                query += " AND investment_transaction_id = ?"
                params.append(filters['transaction_id'])
                criteria['Transaction ID'] = filters['transaction_id']

            if filters['investment_by']:
                query += " AND investment_by = ?"
                params.append(filters['investment_by'])
                criteria['Investment By'] = filters['investment_by']

            if filters['start_date']:
                query += " AND investment_date >= ?"
                params.append(filters['start_date'])
                criteria['Start Date'] = filters['start_date']

            if filters['end_date']:
                query += " AND investment_date <= ?"
                params.append(filters['end_date'])
                criteria['End Date'] = filters['end_date']

            # --------- execute -------------------------------------------------
            conn = sqlite3.connect('finance_app.db')
            c = conn.cursor()
            c.execute(query, params)
            rows = c.fetchall()

            for row in rows:
                (investment_id, invested_amount, source, loan_from, investment_by,
                 rate, status, investment_date, repay_date,
                 repay_loan, repay_interest) = row

                days = (datetime.now().date() -
                        datetime.strptime(investment_date, '%Y-%m-%d').date()).days
                per_day_interest = (rate / 100 / 30) * invested_amount
                interest_till_date = round(per_day_interest * days, 2)

                summary['total_invested'] += invested_amount or 0
                summary['total_interest'] += interest_till_date or 0
                summary['total_repay_loan'] += repay_loan or 0
                summary['total_repay_interest'] += repay_interest or 0

                results.append([
                    investment_id, status,      # Transaction ID, Status
                    source or '-',              # Source  (now filled)
                    loan_from or '-',           # Loan From
                    investment_by, invested_amount, rate,
                    round(per_day_interest, 2), days, interest_till_date,
                    investment_date, repay_date, repay_loan, repay_interest
                ])

            conn.close()

        return render_template(
            'investment_stats.html',
            results=results,
            criteria=criteria,
            summary=summary
        )

    # ------------------------------------------------------------------
    # Existing detail route unchanged
    # ------------------------------------------------------------------
    @app.route('/investment-details/<transaction_id>')
    def investment_details(transaction_id):
        conn = sqlite3.connect('finance_app.db')
        c = conn.cursor()
        c.execute(
            "SELECT * FROM investments WHERE investment_transaction_id = ?",
            (transaction_id,)
        )
        investment = c.fetchone()
        conn.close()
        return render_template('investment_details.html', investment=investment)
