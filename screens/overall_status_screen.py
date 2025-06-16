# screens/overall_status_screen.py
# ---------------------------------------------------------------
# Overall Status dashboard — Gold Loans, Personal Loans,
# Investments, Expenses (interest calculated inside SQLite).
# ---------------------------------------------------------------
from flask import Blueprint, render_template, request, current_app as app
from db_setup import get_db_connection
from datetime import datetime

# ✅ banner proves THIS file is being imported
print(">>> LOADED Overall-Status blueprint from:", __file__)

# Blueprint Flask will register in app.py
overall_status_bp = Blueprint("overall_status", __name__)


# ----------------------------------------------------------------
# Helper to build optional start/end-date WHERE fragments
# ----------------------------------------------------------------
def _date_filter(column, start, end):
    frag, params = "", []
    if start:
        frag += f" AND {column} >= ?"
        params.append(start)
    if end:
        frag += f" AND {column} <= ?"
        params.append(end)
    return frag, params


@overall_status_bp.route("/overall-status", methods=["GET", "POST"])
def overall_status_view():
    app.logger.info("✅  Entered overall_status_view ----------------------------")

    # -------- read optional date range from form --------
    start_date = end_date = ""
    if request.method == "POST":
        start_date = request.form.get("start_date") or ""
        end_date   = request.form.get("end_date") or ""
    app.logger.info(f"Date filter → start={start_date}  end={end_date}")

    conn = get_db_connection()
    cur  = conn.cursor()

    # ---------------- GOLD LOANS (Open) -----------------
    gold_where, gold_params = _date_filter("pledge_date", start_date, end_date)
    cur.execute(f"""
        SELECT
            COUNT(*)                                    AS open_cnt,
            COALESCE(SUM(loan_amount), 0)               AS sum_loan,
            COALESCE(SUM(
                loan_amount * interest_rate / 100.0 / 30.0 *
                (julianday('now') - julianday(pledge_date))
            ), 0)                                       AS sum_interest
        FROM pledge
        WHERE bill_status = 'Open' {gold_where}
    """, gold_params)
    gold_open, gold_loan_amt, gold_interest = cur.fetchone()

    cur.execute(f"""
        SELECT COUNT(*) FROM pledge
        WHERE bill_status != 'Open' {gold_where}
    """, gold_params)
    gold_closed = cur.fetchone()[0] or 0

    # -------------- PERSONAL LOANS (Open) ---------------
    pl_where, pl_params = _date_filter("loan_date", start_date, end_date)
    cur.execute(f"""
        SELECT
            COUNT(*)                                    AS open_cnt,
            COALESCE(SUM(loan_amount), 0)               AS sum_loan,
            COALESCE(SUM(
                loan_amount * interest_rate / 100.0 / 30.0 *
                (julianday('now') - julianday(loan_date))
            ), 0)                                       AS sum_interest
        FROM personal_loan
        WHERE pbill_status = 'Open' {pl_where}
    """, pl_params)
    per_open, per_loan_amt, per_interest = cur.fetchone()

    cur.execute(f"""
        SELECT COUNT(*) FROM personal_loan
        WHERE pbill_status != 'Open' {pl_where}
    """, pl_params)
    per_closed = cur.fetchone()[0] or 0

    # -------------- PARTNER-WISE INVESTMENTS (Open) --------------
    inv_where, inv_params = _date_filter("investment_date", start_date, end_date)
    cur.execute(f"""
        SELECT investment_by, invested_amount, interest_rate, investment_date
        FROM   investments
        WHERE  investment_status = 'Open' {inv_where}
    """, inv_params)

    from collections import defaultdict
    agg = defaultdict(lambda: {"invested": 0.0, "interest": 0.0})

    for by, invested, rate, inv_date in cur.fetchall():
        days = (datetime.now() - datetime.strptime(inv_date, "%Y-%m-%d")).days
        interest = round((invested * rate / 100 / 30) * days, 2)

        agg[by]["invested"]  += invested
        agg[by]["interest"]  += interest

    partner_data = []
    total_invested = 0.0
    for by, vals in agg.items():
        invested_sum  = round(vals["invested"],  2)
        interest_sum  = round(vals["interest"],  2)
        total_value   = round(invested_sum + interest_sum, 2)

        total_invested += invested_sum
        partner_data.append({
            "investment_by": by,
            "total_invested": invested_sum,
            "interest_till_date": interest_sum,
            "total_value": total_value
        })

    # -------------- repaid + expenses -------------------
    cur.execute("SELECT COALESCE(SUM(repay_loan_amount),0), "
                "       COALESCE(SUM(repay_interest_amount),0) "
                "FROM investments")
    repay_loan, repay_int = cur.fetchone()

    exp_where, exp_params = _date_filter("expense_date", start_date, end_date)
    cur.execute(f"""
        SELECT COALESCE(SUM(amount),0)
        FROM   expenses
        WHERE 1=1 {exp_where}
    """, exp_params)
    total_exp = cur.fetchone()[0]

    conn.close()

    # Log so we can compare with UI
    app.logger.info(f"GOLD → open={gold_open}  loan={gold_loan_amt}  int={gold_interest}")
    app.logger.info(f"PER  → open={per_open}   loan={per_loan_amt}   int={per_interest}")

    # -------------- render template ---------------------
    return render_template(
        "overall_status.html",
        gold_open=gold_open,
        gold_closed=gold_closed,
        gold_loan_amount=round(gold_loan_amt, 2),
        gold_interest=round(gold_interest, 2),
        personal_open=per_open,
        personal_closed=per_closed,
        personal_loan_amount=round(per_loan_amt, 2),
        personal_interest=round(per_interest, 2),
        total_invested=round(total_invested, 2),
        partner_data=partner_data,
        total_repay_loan=round(repay_loan, 2),
        total_repay_interest=round(repay_int, 2),
        total_expenses=round(total_exp, 2),
        start_date=start_date,
        end_date=end_date,
    )
