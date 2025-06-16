
from flask import render_template, request
from db_setup import get_db_connection
from datetime import datetime, timedelta
from flask import Blueprint

def gold_loan_stats_route(app):
    bp = Blueprint('gold_loan_stats', __name__)

    @bp.route('/gold-loan-stats', methods=['GET', 'POST'])
    def gold_loan_stats():
        conn = get_db_connection()
        cursor = conn.cursor()
        results = []
        stats_summary = {
            'total_open': 0,
            'total_release': 0,
            'total_auctioned': 0,
            'sum_loan': 0.0,
            'sum_interest_total': 0.0,
            'sum_interest_collected': 0.0
        }

        if request.method == 'POST':
            status = request.form.get("bill_status")
            start_date = request.form.get("start_date")
            end_date = request.form.get("end_date")
            one_year_filter = request.form.get("one_year")
            interest_filter = request.form.get("interest_80")

            query = """
                SELECT id, bill_number, bill_status, customer_name, customer_phone,
                       pledge_date, loan_amount, interest_rate, received_interest, ornament_name
                FROM pledge
                WHERE 1=1
            """
            params = []

            if status and status != "All":
                query += " AND bill_status = ?"
                params.append(status)

            if start_date and end_date:
                query += " AND pledge_date BETWEEN ? AND ?"
                params.append(start_date)
                params.append(end_date)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            for i, row in enumerate(rows, 1):
                pledge_date = datetime.strptime(row['pledge_date'], '%Y-%m-%d')
                total_days = (datetime.now() - pledge_date).days

                loan_amount = float(row['loan_amount'] or 0)
                interest_rate = float(row['interest_rate'] or 0)
                collected_interest = float(row['received_interest'] or 0)

                interest_per_day = round((loan_amount * interest_rate) / (100 * 30), 2)
                total_interest = round(interest_per_day * total_days, 2)

                include_row = True

                if one_year_filter and pledge_date > datetime.now() - timedelta(days=365):
                    include_row = False

                if interest_filter and total_interest < (0.8 * loan_amount):
                    include_row = False

                if include_row:
                    results.append({
                        'sno': i,
                        'bill_number': row['bill_number'],
                        'bill_status': row['bill_status'],
                        'customer_name': row['customer_name'],
                        'customer_phone': row['customer_phone'],
                        'ornament_name': row['ornament_name'],
                        'pledge_date': pledge_date.strftime('%Y-%m-%d'),
                        'loan_amount': loan_amount,
                        'total_days': total_days,
                        'interest_rate': interest_rate,
                        'interest_per_day': interest_per_day,
                        'total_interest': total_interest,
                        'collected_interest': collected_interest
                    })

                    stats_summary['sum_loan'] += loan_amount
                    stats_summary['sum_interest_total'] += total_interest
                    stats_summary['sum_interest_collected'] += collected_interest

                    if row['bill_status'] == "Open":
                        stats_summary['total_open'] += 1
                    elif row['bill_status'] == "Release":
                        stats_summary['total_release'] += 1
                    elif row['bill_status'] == "Auctioned":
                        stats_summary['total_auctioned'] += 1

        conn.close()
        return render_template('gold_loan_stats.html', results=results, stats=stats_summary)

    @bp.route('/gold-loan/view/<bill_number>', methods=['GET'])
    def view_pledge_details(bill_number):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pledge WHERE bill_number = ?", (bill_number,))
        pledge = cursor.fetchone()
        conn.close()
        return render_template('gold_loan_detail.html', pledge=pledge)

    app.register_blueprint(bp)
