from flask import Flask, make_response, render_template, request, redirect, url_for, flash, jsonify, session
from dotenv import load_dotenv

from time import sleep

from Controllers.customer_controller import addCustomer, addRewardPoints, getCustomerById, subtractRewardPoints
from Controllers.cart_controller import addCart
from Controllers.cart_item_controller import addPayment as addCartItem
from Controllers.payment_controller import addPayment
from Controllers.product_controller import getProductWithUpc, getProductWithEpc, getProductWithId
from Controllers.inventory_controller import removeInventory, searchInventory

from decimal import Decimal, ROUND_HALF_UP

# from Services.fan_service import turnOnFan
# from Services.fan_service import turnOffFan

from Models.product import Product

# from Services.email_service import sendEmail
# from Services.email_service import readEmail

# import paho.mqtt.client as mqtt

# import fanControl
import os

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY') or "supersecretfallbackkey"



# app = Flask(__name__)
# app.secret_key = os.getenv('FLASK_SECRET_KEY')

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

    products = Product.get_allProducts()
    print(products)
    
    return render_template('index.html', fridges=fridge_data,products=products)

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
    if 'membership_number' not in session:
        flash("Please enter your membership number first.")
        return redirect(url_for('index'))

    def to_decimal(v):
        if isinstance(v, Decimal):
            return v
        return Decimal(str(v))
    
    subtotal = Decimal('0.00') if not items else sum(to_decimal(item.get('total', 0)) for item in items)
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

@app.route('/get-reward-points')
def get_reward_points():
    membership_number = session.get('membership_number')
    if not membership_number:
        return jsonify({"status": "error", "message": "No membership number in session"}), 400

    success, customer = getCustomerById(membership_number)
    if not success:
        return jsonify({"status": "error", "message": "Customer not found"}), 404

    return jsonify({
        "status": "success",
        "points": customer.total_reward_points
    })

@app.route('/finalize-payment', methods=['POST'])
def finalize_payment():
    data = request.get_json() or {}
    card_number = data.get('cardNumber') or data.get('card')
    expiry = data.get('expiryDate') or data.get('expiry')

    use_points = request.get_json().get('usePoints') == True

    # Apply discount
    if use_points and membership_number:
        success, customer = getCustomerById(membership_number)
        if success:
            points = customer.total_reward_points
            discount = Decimal(points // 100)
            total = max(total - discount, Decimal('0.00'))
            points_used = int(discount * 100)
            subtractRewardPoints(membership_number, points_used)


    # membership number (if scanned earlier) is kept in session
    membership_number = session.get('membership_number')

    # Simulate payment processing (no real gateway here)
    print('Finalizing payment. Card:', card_number, 'Expiry:', expiry, 'Membership:', membership_number)

    # Remove inventory for each item (existing behavior)
    for item in items:
        try:
            removeInventory(item["id"], 1, item["quantity"])
        except Exception as e:
            print('Warning: failed to remove inventory for', item, e)

    # Calculate totals
    def to_decimal(v):
        return Decimal(str(v)) if not isinstance(v, Decimal) else v
    
    subtotal = sum(to_decimal(item.get('total', 0)) for item in items)
    gst = (subtotal * GST_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    qst = (subtotal * QST_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total = (subtotal + gst + qst).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    reward_points = int(subtotal // Decimal('10') * 100)

    customer_success, customer_result = addRewardPoints(membership_number, reward_points)
    if not customer_success:
        return jsonify({"status": "error", "message": customer_result}), 400
    
    # Create cart using the cart controller
    cart_success, cart_result = addCart(membership_number, float(total), reward_points)
    if not cart_success:
        return jsonify({"status": "error", "message": cart_result}), 400

    # Get cart ID from the result
    cart_id = cart_result
    print('Cart id: ', cart_id)
    
    # Create cart items for each product
    for item in items:
        cart_item_success, cart_item_message = addCartItem(
            cart_id=cart_id,
            product_id=item['id'],
            quantity=item['quantity'],
            total_price=float(item['total'])
        )
        if not cart_item_success:
            return jsonify({"status": "error", "message": cart_item_message}), 400
    
    # Create payment record
    payment_success, payment_message = addPayment(cart_id, card_number, expiry)

    # Clear cart and membership
    items.clear()
    session.pop('membership_number', None)

    return jsonify({"status": "success", "message": "Payment processed (simulated)"})

@app.route('/scan', methods=['POST'])
def scan_item():
    data = request.get_json() or {}
    code = data.get('code') or data.get('itemCode') or data.get('upc') or data.get('epc')
    if isinstance(code, str) and len(code) == 13 and code.startswith("0"):
        code = code[1:]

    if not code:
        return jsonify({"status": "error", "message": "No code provided"}), 400

    product = getProductWithUpc(code)
    if not product:
        product = getProductWithEpc(code)

    if product and hasattr(product, 'productId'):
        unit_price = float(product.price)
        product_id = product.productId

        # Check if item already exists in the list
        for item in items:
            if item['id'] == product_id:
                item['quantity'] += 1
                item['total'] = item['quantity'] * unit_price
                return jsonify({"status": "success", "item": item, "items": items})

        # If not found, add as new item
        new_item = {
            'id': product_id,
            'name': product.name,
            'quantity': 1,
            'unit': unit_price,
            'total': unit_price,
        }
        items.append(new_item)
        return jsonify({"status": "success", "item": new_item, "items": items})
    else:
        return jsonify({"status": "error", "message": "Item not found"}), 404

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
def update_product():
    productId = request.form.get('productId')
    new_name = request.form.get('name')
    new_type = request.form.get('type')
    new_price = request.form.get('price')
    new_expirationDate = request.form.get('expirationDate')
    new_manufacturerName = request.form.get('manufacturerName')
    new_upc = request.form.get('upc')
    new_epc = request.form.get('epc')
    new_quantity = request.form.get('quantity');

    result, message = Product.update_product(productId=productId, new_name=new_name,
                                            new_type=new_type,new_price=new_price,
                                            new_expirationDate=new_expirationDate,new_manufacturerName=new_manufacturerName,
                                            new_upc=new_upc,new_epc=new_epc,
                                            new_quantity=new_quantity
                                            )
    print(message);
    return redirect(url_for('index'))

@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form.get('name')
    type_ = request.form.get('type')
    price = request.form.get('price')
    expirationDate = request.form.get('expirationDate')
    manufacturerName = request.form.get('manufacturerName')
    upc = request.form.get('upc')
    epc = request.form.get('epc')
    quantity = request.form.get('quantity');
    quantity = 0 if quantity is None else request.form.get('quantity');

    message = Product.create(name=name, type_=type_,price=price,
                            expiration_date=expirationDate,manufacturer_name=manufacturerName,
                            upc=upc,epc=epc,quantity = quantity
                            )
    print(message);
    return redirect(url_for('index'))

@app.route('/delete_product', methods=['POST'])
def delete_product():
    productId = request.form.get('productId')
    print("productID is :" + productId)
    message = Product.delete_product(productId=productId)
    print(message);
    return redirect(url_for('index'))

@app.route('/clear-cart', methods=['GET'])
def clear_cart():
    items.clear()
    session.pop('membership_number', None)
    return jsonify({"status": "success"})

@app.route('/search-item', methods=['POST'])
def search_item():
    data = request.get_json()
    code = data.get("code")

    if not code:
        return jsonify({"status": "error", "message": "No code provided"}), 400

    result, inventory_item_id = searchInventory(code, 1) # 1 is the location id

    if inventory_item_id:
        product = getProductWithId(inventory_item_id)

        if product and hasattr(product, 'productId'):
            unit_price = float(product.price)
            product_id = product.productId
            
            # Check if item already exists in the list
            for item in items:
                if item['id'] == product_id:
                    item['quantity'] += 1
                    item['total'] = item['quantity'] * unit_price
                    return jsonify({"status": "success", "item": item, "items": items})

            # If not found, add as new item
            new_item = {
                'id': product_id,
                'name': product.name,
                'quantity': 1,
                'unit': unit_price,
                'total': unit_price,
            }
            items.append(new_item)
            return jsonify({"status": "success", "item": new_item, "items": items})
        else:
            return jsonify({"status": "error", "message": "Item not found"}), 404
    else:
        return jsonify({"status": "error", "message": "Item not found"}), 404
    
@app.route('/customer_page')
def customerPage():
    return render_template('customerPage.html')

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


