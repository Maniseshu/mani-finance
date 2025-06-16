# screens/gold_loan_screen.py
import os
import sqlite3
from flask import request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from datetime import datetime

def gold_loan_route(app):
    UPLOAD_FOLDER = 'uploads/pledge_images'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    @app.route('/gold-loan', methods=['GET', 'POST'])
    def gold_loan():
        if 'username' not in request.cookies and 'username' not in app.session_interface.open_session(app, request):
            return redirect(url_for('login'))

        last_bill = ""
        conn = sqlite3.connect('finance_app.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS pledge (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        customer_name TEXT,
                        customer_phone TEXT,
                        ornament_name TEXT,
                        gross_weight REAL,
                        net_weight REAL,
                        loan_amount REAL,
                        interest_rate REAL,
                        pledge_date TEXT,
                        bill_number TEXT,
                        bill_status TEXT,
                        pledge_remarks TEXT,
                        customer_image TEXT,
                        ornament_image TEXT,
                        proof_image TEXT
                    )''')
        c.execute("SELECT bill_number FROM pledge ORDER BY id DESC LIMIT 1")
        row = c.fetchone()
        if row:
            last_bill = row[0]
        conn.close()

        if request.method == 'POST':
            customer_name = request.form['customer_name']
            customer_phone = request.form['customer_phone']
            ornament_name = request.form['ornament_name']
            gross_weight = request.form['gross_weight']
            net_weight = request.form['net_weight']
            loan_amount = request.form['loan_amount']
            interest_rate = request.form['interest_rate']
            pledge_date = request.form['pledge_date']
            bill_number = request.form['bill_number']
            bill_status = request.form['bill_status']
            pledge_remarks = request.form['pledge_remarks']

            # Initialize file paths as empty
            customer_image_path = ""
            ornament_image_path = ""
            proof_image_path = ""

            customer_image = request.files.get('customer_image')
            if customer_image and customer_image.filename:
                customer_filename = secure_filename(customer_image.filename)
                customer_image_path = f"uploads/pledge_images/{customer_filename}"
                customer_image.save(os.path.join(UPLOAD_FOLDER, customer_filename))

            ornament_image = request.files.get('ornament_image')
            if ornament_image and ornament_image.filename:
                ornament_filename = secure_filename(ornament_image.filename)
                ornament_image_path = f"uploads/pledge_images/{ornament_filename}"
                ornament_image.save(os.path.join(UPLOAD_FOLDER, ornament_filename))

            proof_image = request.files.get('proof_image')
            if proof_image and proof_image.filename:
                proof_filename = secure_filename(proof_image.filename)
                proof_image_path = f"uploads/pledge_images/{proof_filename}"
                proof_image.save(os.path.join(UPLOAD_FOLDER, proof_filename))

            conn = sqlite3.connect('finance_app.db')
            c = conn.cursor()
            c.execute('''INSERT INTO pledge (
                            customer_name, customer_phone, ornament_name, gross_weight, net_weight,
                            loan_amount, interest_rate, pledge_date, bill_number, bill_status,
                            pledge_remarks, customer_image, ornament_image, proof_image
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (customer_name, customer_phone, ornament_name, gross_weight, net_weight,
                       loan_amount, interest_rate, pledge_date, bill_number, bill_status,
                       pledge_remarks, customer_image_path, ornament_image_path, proof_image_path))
            conn.commit()
            conn.close()

            flash('Gold loan pledge submitted successfully!', 'success')
            return redirect(url_for('gold_loan'))

        return render_template('gold_loan.html', today=datetime.today().strftime('%Y-%m-%d'), last_bill=last_bill)
