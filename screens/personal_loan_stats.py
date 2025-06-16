from flask import Blueprint, render_template, request
from db_setup import get_db_connection
from datetime import datetime

personal_loan_stats = Blueprint('personal_loan_stats', __name__)

@personal_loan_stats.route('/personal-loan-stats', methods=['GET', 'POST'])
def personal_loan_stats_view():
    results = []
    stats = {'sum_loan': 0, 'sum_interest_total': 0, 'sum_repay': 0, 'sum_received_interest': 0}

    if request.method == 'POST':
        pbill_status = request.form.get('pbill_status')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        interest_80 = request.form.get('interest_80')

        print("🟢 Entered personal_loan_stats_view()")
        print(f"📨 POST request received")
        print(f"🔍 Filters - Status: {pbill_status} | Start: {start_date} | End: {end_date} | 80% Filter: {interest_80}")

        query = "SELECT * FROM personal_loan WHERE 1=1"
        params = []

        if pbill_status and pbill_status != 'All':
            query += " AND pbill_status = ?"
            params.append(pbill_status)

        if start_date:
            query += " AND loan_date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND loan_date <= ?"
            params.append(end_date)

        print("🧮 Final Query:", query)
        print("📦 Params:", params)

        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute(query, params).fetchall()

        print("📊 Rows fetched:", len(rows))

        for row in rows:
            total_days = (datetime.today() - datetime.strptime(row['loan_date'], '%Y-%m-%d')).days
            interest_per_day = (row['loan_amount'] * row['interest_rate']) / 100 / 30
            total_interest = round(interest_per_day * total_days, 2)

            if interest_80 and total_interest < 0.8 * row['loan_amount']:
                continue

            results.append({
                'pbill_number': row['pbill_number'],
                'pbill_status': row['pbill_status'],
                'customer_name': row['customer_name'],
                'customer_phone': row['customer_phone'],
                'loan_date': row['loan_date'],
                'loan_amount': row['loan_amount'],
                'interest_rate': row['interest_rate'],
                'total_days': total_days,
                'interest_per_day': round(interest_per_day, 2),
                'total_interest': total_interest,
                'repay_date': row['repay_date'],
                'repay_amount': row['repay_amount'],
                'received_interest': row['received_interest']
            })

            stats['sum_loan'] += row['loan_amount'] or 0.0
            stats['sum_interest_total'] += total_interest or 0.0
            stats['sum_repay'] += row['repay_amount'] or 0.0
            stats['sum_received_interest'] += row['received_interest'] or 0.0

        conn.close()
        print("✅ Processing complete. Results count:", len(results))

    return render_template('personal_loan_stats.html', results=results, stats=stats)
