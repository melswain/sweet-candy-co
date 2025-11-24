import os

from flask import Flask, make_response, render_template, request, redirect, url_for, flash, jsonify, session
from dotenv import load_dotenv
from time import sleep
from decimal import Decimal, ROUND_HALF_UP
import paho.mqtt.client as mqtt

from Controllers.customer_controller import addCustomer, customer_login, getCustomerData, register_customer
from Controllers.cart_controller import getCustomerCartHistory
from Controllers.product_controller import getAllProducts
from Controllers.inventory_controller import getInventory

from Services.checkout_service import calculate_checkout
from Services.fan_service import toggle_fan
from Services.reward_service import get_points
from Services.payment_service import process_payment
from Services.scan_service import process_scan
from Services.product_service import update_product, add_product, get_all_products
from Services.search_service import search_item
from Services.epc_reader_service import handle_rfid
from Services.temperature_readings_service import handle_temperature, update_sensor_data

# from Services.fan_service import turnOnFan
# from Services.fan_service import turnOffFan

# from Services.email_service import sendEmail
# from Services.email_service import readEmail

# import fanControl

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

current_fan_state = False

#MQTT setup
sensor_data = {
    "Frig1": {"temperature": 1, "humidity": 30},
    "Frig2": {"temperature": 0, "humidity": 50}
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

    if topic == "rfid/scan/store1":
        handle_rfid(payload)
    elif topic == "environment/store1/temperature":
        handle_temperature(payload)
    elif topic.startswith("Frig"):
        update_sensor_data(sensor_data, topic, payload)
    else:
        print(f"Unhandled topic {topic}: {payload}")


# Initialize MQTT client for the Flask app so incoming messages update sensor_data
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
    print('MQTT client started and listening')
except Exception as e:
    print('Failed to start MQTT client:', e)

# Optionally start the serial EPC reader that publishes to the MQTT broker.
from Services.epc_reader_service import start_epc_reader
if os.getenv('START_EPC_READER', '0') == '1':
    try:
        start_epc_reader()
        print('Started serial EPC reader (background thread)')
    except Exception as e:
        print('Failed to start serial EPC reader:', e)

# mqtt_client = mqtt.Client()
# mqtt_client.on_connect = on_connect
# mqtt_client.on_message = on_message
# mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
# mqtt_client.loop_start()  # run in background

GST_RATE = Decimal('0.05')
QST_RATE = Decimal('0.09975')

items = [
        # {'id': 1,'name': 'Chocolate Dream Bar', 'quantity': 4, 'unit': 3.99, 'total': 15.96},
        # {'id': 2, 'name': 'Rainbow Sour Strips', 'quantity': 1, 'unit': 4.50, 'total': 4.50},
        # {'id': 3, 'name': 'Peanut Butter Cups 4pk', 'quantity': 1, 'unit': 5.99, 'total': 5.99}
    ]

def format_money(d: Decimal) ->str:
    return f"{d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}"

@app.route('/dashboard')
def index():
    fridge_data = [
        {
        'name': 'Frig1', 
        'temperature': sensor_data['Frig1']['temperature'] or 'N/A',
        'humidity': sensor_data['Frig1']['humidity'] or 'N/A'
        },
        {
        'name' : 'Frig2',
        'temperature': sensor_data['Frig2']['temperature'] or 'N/A',
        'humidity': sensor_data['Frig2']['humidity'] or 'N/A'
        }
    ]

    products = getAllProducts()
    success, inventory = getInventory()
    
    return render_template('index.html', fridges=fridge_data,products=products,inventory=inventory)

@app.route('/add', methods=['POST'])
def add():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')

    success, message = addCustomer(name, email, phone)

    return {"success": success, "message": message}

@app.route('/sensor_data')
def get_sensor_data():
    return jsonify(sensor_data)

@app.route('/fan', methods=['POST'])
def toggle():
    data = request.get_json()
    enabled = data.get('enabled')

    success, message = toggle_fan(enabled)

    return {"success": success, "message": message}

@app.route('/checkout')
def checkout():
    summary = calculate_checkout(items)
    return render_template('customers.html', **summary, format_money=format_money)

@app.route('/submit-membership', methods=['POST'])
def submit_membership():
    data = request.get_json()
    membership_number = data.get('membershipNumber')
    session['membership_number'] = membership_number

    return {"status": "success", "membership": membership_number}

@app.route('/get-membership')
def get_membership():
    membership_number = session.get('membership_number')
    return {"status": "success", "membership_number": membership_number}

@app.route('/get-reward-points', methods=['GET'])
def get_reward_points():
    membership_number = session.get('membership_number')
    if not membership_number:
        return jsonify({"status": "error", "message": "No membership number in session"}), 400

    result = get_points(membership_number)
    return jsonify(result["body"]), result["status"]

@app.route('/finalize-payment', methods=['POST'])
def finalize_payment():
    data = request.get_json() or {}
    card_number = data.get('cardNumber') or data.get('card')
    expiry = data.get('expiryDate') or data.get('expiry')
    use_points = session.get('usePoints')
    membership_number = session.get('membership_number')

    if not membership_number:
        return jsonify({"status": "error", "message": "No membership number in session"}), 400

    result = process_payment(items, membership_number, card_number, expiry, use_points)

    return jsonify(result["body"]), result["status"]

@app.route('/set-use-points', methods=['POST'])
def set_use_points():
    session['usePoints'] = 'true'
    return jsonify({'status': 'ok'})

@app.route('/scan', methods=['POST'])
def scan_item():
    data = request.get_json() or {}
    code = data.get('code') or data.get('itemCode') or data.get('upc')

    if not code:
        return jsonify({"status": "error", "message": "No code provided"}), 400

    result = process_scan(code, items)
    return jsonify(result["body"]), result["status"]

@app.route('/cart-items', methods=['GET'])
def get_cart_items():
    return jsonify({"items": items})

@app.route('/remove-item', methods=['POST'])
def remove_item():
    data = request.get_json() or {}
    item_id = data.get('id')
    if not item_id:
        return jsonify({"status": "error", "message": "No item ID provided"}), 400

    try:
        item_id = int(item_id)
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid item ID"}), 400

    global items
    items = [item for item in items if item['id'] != item_id]
    return jsonify({"status": "success", "items": items})

@app.route('/update_product', methods=['POST'])
def update_products():
    data = request.form.to_dict()
    print(data)
    result = update_product(data)

    return result

@app.route('/add_product', methods=['POST'])
def create_new_product():
    data = request.form.to_dict()
    status, message, id = add_product(data)

    return jsonify({"status": status, "message": message, "id": id}), 400

@app.route('/products', methods=['GET'])
def get_products():
    products = get_all_products()
    return jsonify(products)

@app.route('/clear-cart', methods=['GET'])
def clear_cart():
    session.clear()
    items.clear()
    return jsonify({"status": "success"})

@app.route('/search-item', methods=['POST'])
def search():
    global items
    data = request.get_json() or {}
    code = data.get("code")

    if not code:
        return jsonify({"status": "error", "message": "No code provided"}), 400

    status, item, items = search_item(code, items)

    if status == "success":
        return jsonify({"status": "success", "item": item, "items": items})
    else:
        return jsonify({"status": "error", "message": "Item not found"}), 404

@app.route('/customer_page')
def customerPage():
    if 'customer_id' not in session:
        return redirect('/login')
    
    membership_number = session.get('membership_number')
    
    if not membership_number:
        return jsonify({"status": "error", "message": "No membership number in session"}), 401
    
    success, customer_data = getCustomerData(membership_number)
    success1, cart_history_data = getCustomerCartHistory(membership_number)
    
    if success:
        return render_template('customerPage.html', customer_data = customer_data, cart_history_data=cart_history_data)
    else:
        return print(customer_data), 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        success, msg = customer_login(username, password)
        if success:
            session['customer_id'] = username
            session['membership_number'] = username
            return redirect(url_for('customerPage'))
        flash(msg)
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login')) 

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    customer_id = data.get('customerId') or request.form.get('username')
    password = data.get('password') or request.form.get('password')

    if not customer_id or not password:
        return jsonify({'status': 'error', 'message': 'Missing customerId or password'}), 400

    success, msg = register_customer(customer_id, password)
    if success:
        return jsonify({'status': 'success', 'message': msg})
    return jsonify({'status': 'error', 'message': msg}), 400

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