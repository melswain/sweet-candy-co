from flask import Flask, make_response, render_template, request, redirect, url_for, flash, jsonify, session
from dotenv import load_dotenv

from time import sleep

from Controllers.customer_controller import addCustomer

from decimal import Decimal, ROUND_HALF_UP

from Controllers.product_controller import getProductWithUpc, getProductWithEpc
from Controllers.inventory_controller import removeInventory
# from Services.fan_service import turnOnFan
# from Services.fan_service import turnOffFan

# from Services.email_service import sendEmail
# from Services.email_service import readEmail

# import paho.mqtt.client as mqtt

# import fanControl
import os



app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

current_fan_state = False

#MQTT setup
sensor_data = {
    "Frig1": {"temperature": 50, "humidity": None},
    "Frig2": {"temperature": None, "humidity": None}
}

MQTT_BROKER = "172.20.10.12"  
MQTT_PORT = 1883

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code "+str(rc))
    client.subscribe("Frig1/#")
    client.subscribe("Frig2/#")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    if topic.startswith("Frig1"):
        if "temperature" in topic:
            sensor_data["Frig1"]["temperature"] = payload
        elif "humidity" in topic:
            sensor_data["Frig1"]["humidity"] = payload
    elif topic.startswith("Frig2"):
        if "temperature" in topic:
            sensor_data["Frig2"]["temperature"] = payload
        elif "humidity" in topic:
            sensor_data["Frig2"]["humidity"] = payload

# mqtt_client = mqtt.Client()
# mqtt_client.on_connect = on_connect
# mqtt_client.on_message = on_message
# mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
# mqtt_client.loop_start()  # run in background

GST_RATE = Decimal('0.05')
QST_RATE = Decimal('0.09975')

items = [
        {'id': 1,'name': 'Chocolate Dream Bar', 'quantity': 4, 'unit': 3.99, 'total': 15.96},
        {'id': 2, 'name': 'Rainbow Sour Strips', 'quantity': 1, 'unit': 4.50, 'total': 4.50},
        {'id': 3, 'name': 'Peanut Butter Cups 4pk', 'quantity': 1, 'unit': 5.99, 'total': 5.99}
    ]

def format_money(d: Decimal) ->str:
    return f"{d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}"

def process_membership(membership_number):
    # Your logic here
    print(f"Processing membership: {membership_number}")
    return {"status": "success", "points": 26}

@app.route('/')
def index():
    fridge_data = [
        {
        'name': 'Fridge 1', 
        'temperature': sensor_data['Frig1']['temperature'] or 'N/A',
        'humidity': sensor_data['Frig1']['humidity'] or 'N/A'
        },
        {
        'name' : 'Fridge 2',
        'temperature': sensor_data['Frig2']['temperature'] or 'N/A',
        'humidity': sensor_data['Frig2']['humidity'] or 'N/A'
        }
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

@app.route('/sensor_data')
def get_sensor_data():
    return sensor_data  # Flask will convert your dict to JSON


@app.route('/fan', methods=['POST'])
def toggle():
    data = request.get_json()
    enabled = data.get('enabled')
    if enabled:
        success, message =turnOnFan()
    else:
        success, message =turnOffFan()
    print(f"Switch is now {'ON' if enabled else 'OFF'}")

    # success, message =turnOnFan() 
    return redirect('/'), message

@app.route('/checkout')
def checkout():
    def to_decimal(v):
        if isinstance(v, Decimal):
            return v
        return Decimal(str(v))
    
    subtotal = Decimal('0.00') if not items else sum(to_decimal(item.get('total', 0)) for item in items)
    gst = (subtotal * GST_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    qst = (subtotal * QST_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total = (subtotal + gst + qst).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # Reward points: 1 point per $10
    reward_points = int(subtotal // Decimal('10'))

    return render_template('customers.html',
                           items=items,
                           subtotal=subtotal,
                           gst=gst,
                           qst=qst,
                           total=total,
                           reward_points=reward_points,
                           format_money=format_money)

@app.route('/submit-membership', methods=['POST'])
def submit_membership():
    data = request.get_json()
    membership_number = data.get('membershipNumber')

    response = make_response(jsonify({"status": "success", "membership": membership_number}))
    session['membership_number'] = membership_number
    return response

@app.route('/get-membership')
def get_membership():
    membership_number = session.get('membership_number')
    response = make_response(jsonify({"status": "success", "membership_number": membership_number}))
    return response

@app.route('/finalize-payment')
def clear():
    session.pop('membership_number', None)
    for item in items:
        removeInventory(item["id"], 1, item["quantity"])
    
    # Use the cart controller to create a cart using the membership number, total price, and reward points
    # For every removed item, get its ID
    # For every item id, create a cart item with the cart item controller using the cart id, product id, quantity, and price
    # Create a payment with the payment controller using the cart id, card number, and card expiry date

    items.clear()
    response = make_response(jsonify({"status": "success"}))
    return response

@app.route('/scan', methods=['POST'])
def scan_item():
    data = request.get_json() or {}
    # support different keys from JS bridge or RFID bridge
    code = data.get('code') or data.get('itemCode') or data.get('upc') or data.get('epc')
    if not code:
        return jsonify({"status": "error", "message": "No code provided"}), 400

    # first try UPC, then EPC
    product = getProductWithUpc(code)
    if not product:
        product = getProductWithEpc(code)

    if product and hasattr(product, 'productId'):
        unit_price = float(product.price)
        item = {
            'id': product.productId,
            'name': product.name,
            'quantity': 1,
            'unit': unit_price,
            'total': unit_price * 1,
        }
        items.append(item)
        return jsonify({"status": "success", "item": item, "items": items})
    else:
        return jsonify({"status": "error", "message": "Item not found"}), 404

@app.route('/cart-items', methods=['GET'])
def get_cart_items():
    return jsonify({"items": items})

# constantly checks for temperature of fridges
# temp1 = sensor_data['Frig1'].get('temperature', '0')
# temp2 = sensor_data['Frig2'].get('temperature', '0')

# if temp1 == None:
#     temp1 = 0
# else:
#     temp1 = int(sensor_data['Frig1'].get('temperature', '0'))


# if temp2 == None:
#     temp2 = 0
# else:
#     temp2 = int(sensor_data['Frig2'].get('temperature', '0'))

# if  temp1 >= 40 or  temp2 >= 40 :
#     sendEmail()
#     sleep(15)
#     response = readEmail()
#     if response:
#         turnOnFan()
    




if __name__ == '__main__':
    app.run(debug=True)
