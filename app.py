from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from decimal import Decimal, ROUND_HALF_UP

from Controllers.customer_controller import addCustomer
from Services.fan_service import turnOnFan
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

GST_RATE = Decimal('0.05')
QST_RATE = Decimal('0.09975')

def format_money(d: Decimal) ->str:
    return f"{d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}"

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
    print('Add route')
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')

    success = addCustomer(name, email, phone)
    return redirect('/') if success else "Error adding customer"

@app.route('/fan', methods=['POST'])
def toggle():
    data = request.get_json()
    enabled = data.get('enabled')
    print(f"Switch is now {'ON' if enabled else 'OFF'}")

    success, message = turnOnFan()
    return redirect('/'), message
    # KISHAAN: add fan state logic function here
    # return f"Switch state updated to {'ON' if enabled else 'OFF'}"

@app.route('/checkout')
def checkout():
    # placeholder data for fridge temperature and humidity values
    items = [
        {'name': 'Grape Lollipop', 'quantity': 4, 'unit': 3.99, 'total': 15.96},
        {'name': '500g Assorted Jolly Ranchers', 'quantity': 1, 'unit': 6.50, 'total': 6.50}
    ]

    def to_decimal(v):
        if isinstance(v, Decimal):
            return v
        return Decimal(str(v))
    
    subtotal = sum(to_decimal(item['total']) for item in items)
    gst = (subtotal * GST_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    qst = (subtotal * QST_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total = (subtotal + gst + qst).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # Reward points: 1 point per $10
    reward_points = int(subtotal // Decimal('10') * 100)

    return render_template('customers.html',
                           items=items,
                           subtotal=subtotal,
                           gst=gst,
                           qst=qst,
                           total=total,
                           reward_points=reward_points,
                           format_money=format_money)

if __name__ == '__main__':
    app.run(debug=True)