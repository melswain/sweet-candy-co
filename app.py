from flask import Flask, render_template, request, redirect
from dotenv import load_dotenv
# Comment out this line when testing
from Controllers.customer_controller import addCustomer
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

@app.route('/')
def index():
    # placeholder data for fridge temperature and humidity values
    fridge_data = [
        {'name': 'Fridge 1', 'humidity': '45%', 'temperature': '25°C'},
        {'name': 'Fridge 2', 'humidity': '50%', 'temperature': '5°C'}
    ]
    return render_template('index.html', fridges=fridge_data)

@app.route('/add', methods=['POST'])
def add():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')

    # When not using Pi, use this for testing
    # flash(f'Added {name} ({email}, {phone}) successfully!')
    # return redirect(url_for('index'))

    success = addCustomer(name, email, phone)
    return redirect('/') if success else "Error adding customer"

@app.route('/fan', methods=['POST'])
def toggle():
    data = request.get_json()
    enabled = data.get('enabled')
    print(f"Switch is now {'ON' if enabled else 'OFF'}")
    # KISHAAN: add fan state logic function here
    return f"Switch state updated to {'ON' if enabled else 'OFF'}"

if __name__ == '__main__':
    app.run(debug=True)