from flask import Flask, send_from_directory, session, redirect, url_for
from db_setup import init_db
from screens.login_screen import login_route
from screens.gold_loan_screen import gold_loan_route
from screens.personal_loan_screen import personal_loan_route
from screens.release_transaction_screen import release_transaction_route
from screens.expenses_screen import expenses_route
from screens.add_investment_screen import add_investment_route
from screens.repay_investment_screen import repay_investment_route
from screens.repay_personal_loan_screen import repay_personal_loan_route
from screens.daily_transactions import daily_transactions_route
from screens.investment_stats import investment_stats_route
from screens.gold_loan_stats_screen import gold_loan_stats_route
from screens.personal_loan_stats import personal_loan_stats
from screens.overall_status_screen import overall_status_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize the database and register screen routes
init_db()
login_route(app)
gold_loan_route(app)
personal_loan_route(app)
release_transaction_route(app)
expenses_route(app)
add_investment_route(app)
repay_investment_route(app)
repay_personal_loan_route(app)
daily_transactions_route(app)
investment_stats_route(app)
gold_loan_stats_route(app)
app.register_blueprint(personal_loan_stats)
app.register_blueprint(overall_status_bp)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

@app.route('/')
def home_redirect():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    # ▶▶ Runs on http://127.0.0.1:5050
    app.run(debug=True, port=5050)
