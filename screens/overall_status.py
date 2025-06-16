# screens/overall_status.py  –  FINAL, with wrapper + banner
from flask import Blueprint, render_template, request, current_app as app
from db_setup import get_db_connection
from datetime import datetime

# ------------------------------------------------------------------
# Helper to calculate interest inside SQLite (robust + 1 query)
# ------------------------------------------------------------------
def _date_filter(column, start, end):
    frag, params = "", []
    if start:
        frag += f" AND {column} >= ?"
        params.append(start)
    if end:
        frag += f" AND {column} <= ?"
        params.append(end)
    return frag, params


# ------------------------------------------------------------------
# Blueprint (registered by overall_status_route(app))
# ------------------------------------------------------------------
overall_status = Blueprint("overall_status", __name__)


@overall_status.route("/overall-status", methods=["GET", "POST"])
def overall_status_view():
    # ✅ Banner so we know THIS file is running
    app.logger.info("✅  Entered NEW overall_status_view -------------------------")

    # ---------- read optional date range ---------- #
    start_date = end_date = ""
    if request.method == "POST":
        start_date = request.form.get("start_date") or ""
        end_date   = request.form.get("end_date")   or ""
    app.logger.info(f"Date filter → start={start_date}  end={end_date}")

    conn = get_db_connection()
    cur  = conn.cursor()

    # ---------- GOLD LOAN (open) aggregates -------- #
    gold_where, gold_params = _date_filter("pledge_date", start_date, end_date)
    cur.execute(f"""
        SELECT
            COUNT(*)                                    AS open_count,
            COALESCE(SUM(loan_amount), 0)               AS sum_loan,
            COALESCE(SUM(
                loan_amount * interest_rate / 100.0 / 30.0 *
                (julianday('now') - julianday(pledge_date))
            ), 0)                                       AS sum_interest
        FROM   pledge
        WHERE  bill_status = 'Open' {gold_where}
    """, gold_params)
    gold_open, gold_loan_amount, gold_interest = cur.fetchone()

    cur.execute(f"SELECT COUNT(*) FROM pledge "
                f"WHERE bill_status != 'Open' {gold_where}",
                gold_params)
    gold_closed = cur.fetchone()[0] or 0

    # ---------- PERSONAL LOAN (open) aggregates ---- #
    pl_where, pl_params = _date_filter("loan_date", start_date, end_date)
    cur.execute(f"""
        SELECT
            COUNT(*)                                    AS open_count,
            COALESCE(SUM(loan_amount), 0)               AS sum_loan,
            COALESCE(SUM(
                loan_amount * interest_rate / 100.0 / 30.0 *
                (julianday('now') - julianday(loan_date))
            ), 0)                                       AS sum_interest
        FROM   personal_loan
        WHERE  pbill_status = 'Open' {pl_where}
    """, pl_params)
    personal_open, personal_loan_amount, personal_interest = cur.fetchone()

    cur.execute(f"SELECT COUNT(*) FROM personal_loan "
                f"WHERE pbill_status != 'Open' {pl_where}",
                pl_params)
    personal_closed = cur.fetchone()[0] or 0

    # ---------- PARTNER-WISE INVESTMENTS ----------- #
    inv_where, inv_params = _date_filter("investment_date", start_date, end_date)
    cur.execute(f"""
        SELECT investment_by,
               invested_amount,
               interest_rate,
               investment_date
        FROM   investments
        WHERE  investment_status = 'Open' {inv_where}
    """, inv_params)

    partner_data = []
    total_invested = 0
    for (by, invested, rate, inv_date) in cur.fetchall():
        days = (datetime.now() - datetime.strptime(inv_date, "%Y-%m-%d")).days
        interest = round((invested * rate / 100 / 30) * days, 2)
        total_invested += invested
        partner_data.append({
            "investment_by": by,
            "total_invested": round(invested, 2),
            "interest_till_date": interest,
            "total_value": round(invested + interest, 2)
        })

    # ---------- repaid + expenses (no date filter) -- #
    cur.execute("SELECT COALESCE(SUM(repay_loan_amount),0), "
                "       COALESCE(SUM(repay_interest_amount),0) "
                "FROM investments")
    total_repay_loan, total_repay_interest = cur.fetchone()

    exp_where, exp_params = _date_filter("expense_date", start_date, end_date)
    cur.execute(f"SELECT COALESCE(SUM(amount),0) "
                f"FROM expenses WHERE 1=1 {exp_where}",
                exp_params)
    total_expenses = cur.fetchone()[0]

    conn.close()

    # LOG core numbers so we can compare with UI
    app.logger.info(f"GOLD  → open={gold_open} sumLoan={gold_loan_amount} interest={gold_interest}")
    app.logger.info(f"PER   → open={personal_open} sumLoan={personal_loan_amount} interest={personal_interest}")

    # ---------- render ---------------------------------- #
    return render_template(
        "overall_status.html",
        gold_open=gold_open,
        gold_closed=gold_closed,
        gold_loan_amount=round(gold_loan_amount, 2),
        gold_interest=round(gold_interest, 2),
        personal_open=personal_open,
        personal_closed=personal_closed,
        personal_loan_amount=round(personal_loan_amount, 2),
        personal_interest=round(personal_interest, 2),
        total_invested=round(total_invested, 2),
        partner_data=partner_data,
        total_repay_loan=round(total_repay_loan, 2),
        total_repay_interest=round(total_repay_interest, 2),
        total_expenses=round(total_expenses, 2),
        start_date=start_date,
        end_date=end_date,
    )


# ------------------------------------------------------------------
#  Wrapper so app.py can keep calling overall_status_route(app)
# ------------------------------------------------------------------
def overall_status_route(app_instance):
    """
    Called from app.py exactly the same way your other screens are:
        from screens.overall_status import overall_status_route
        overall_status_route(app)
    """
    app_instance.register_blueprint(overall_status)
    return overall_status
