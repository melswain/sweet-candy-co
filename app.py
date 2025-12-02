import os
import io

from flask import Flask, make_response, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from dotenv import load_dotenv
from time import sleep
from decimal import Decimal, ROUND_HALF_UP
import paho.mqtt.client as mqtt


from Controllers.customer_controller import addCustomer, customer_login, getCustomerData, register_customer
from Controllers.cart_controller import getCustomerCartHistory,getItemPurchaseHistory,getTotalSpending
from Controllers.product_controller import getAllProducts
from Controllers.inventory_controller import getInventory

from Services.checkout_service import calculate_checkout
from Services.fan_service import toggle_fan
from Services.reward_service import get_points
from Services.payment_service import process_payment
from Services.scan_service import process_scan
from Services.product_service import update_product, add_product, get_all_products
from Services.search_service import search_item
from Services.temperature_readings_service import handle_temperature, update_sensor_data
from Services.inventory_report_service import export_inventory_report

from Services.report_service import fetch_sales_rows, generate_csv_bytes, generate_pdf_bytes, parse_date_param
# from Services.cart_report_service import purchase_search_csv, purchase_search_pdf
import Services.cart_report_service as Cart_Report
from flask import send_file, request

# from Services.fan_service import turnOnFan
# from Services.fan_service import turnOffFan

from Services.email_service import sendEmail
from Services.email_service import readEmail

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

items = []
temperatureThreshold = 1
MQTT_BROKER = "localhost"  
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
            print("Frig1"+payload)
            if payload >= temperatureThreshold:
                sendEmail(1)
                readEmail()
        elif "humidity" in topic:
            sensor_data["Frig1"]["humidity"] = payload
    elif topic.startswith("Frig2"):
        if "temperature" in topic:
            sensor_data["Frig2"]["temperature"] = payload
            print("Frig1"+payload)
            if payload >= temperatureThreshold:
                sendEmail(2)
                readEmail()
        elif "humidity" in topic:
            sensor_data["Frig2"]["humidity"] = payload


# Initialize MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
    print('MQTT client started and listening')
except Exception as e:
    print('Failed to start MQTT client:', e)

GST_RATE = Decimal('0.05')
QST_RATE = Decimal('0.09975')

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
def toggle(enable=False):
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
    # If usePoints was set in session it will be a truthy value, but for guests we must disable points
    use_points = session.get('usePoints') if session.get('membership_number') else False
    # Allow guest checkout: if membership_number missing, use 0
    membership_number = session.get('membership_number') or 0
    # Optional receipt email for guests
    receipt_email = data.get('email') or data.get('receiptEmail')

    result = process_payment(items, card_number, expiry, use_points, membership_number, receipt_email)

    return jsonify(result["body"]), result["status"]

@app.route('/set-use-points', methods=['POST'])
def set_use_points():
    session['usePoints'] = 'true'
    return jsonify({'status': 'ok'})

@app.route('/scan', methods=['POST'])
def scan_item():
    data = request.get_json() or {}
    code = data.get('code') or data.get('itemCode') or data.get('upc') or data.get('epc')
    print("CODE: ", code)

    if not code:
        return jsonify({"status": "error", "message": "No code provided"}), 400

    result = process_scan(code, items)
    return jsonify(result)

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
# -----------------------------------------------------------------------------------
#                          Customer Page Route and Methods
# -----------------------------------------------------------------------------------
    
@app.route('/customer_page',methods=['GET','POST'])
def customerPage(before_date=None,after_date=None):
    if 'customer_id' not in session:
        return redirect('/login')
    
    membership_number = session.get('membership_number')
    
    if not membership_number:
        return jsonify({"status": "error", "message": "No membership number in session"}), 401

    success, customer_data = getCustomerData(membership_number)
    success1, cart_history_data = getCustomerCartHistory(membership_number)
    total_spending_success, total_spending = getTotalSpending(
                                            customerId=membership_number
                                        )
    print(total_spending)
    
    if success:
        return render_template('customerPage.html', customer_data = customer_data, cart_history_data=cart_history_data,total_spending=total_spending)
    else:
        return print(customer_data), 404
        
# Experiment
@app.route('/cart_history_filter',methods=["POST"])
def cart_history_filter(before_date=None,after_date=None):
    if 'customer_id' not in session:
        return redirect('/login')
    
    membership_number = session.get('membership_number')
    
    if not membership_number:
        return jsonify({"status": "error", "message": "No membership number in session"}), 401
    
    before_date = request.form.get('date-before')
    after_date = request.form.get('date-after')
    if before_date == "":
        before_date = None
        
    if after_date == "":
        after_date = None

    success_cart, cart_history_data = getCustomerCartHistory(
                                            customerId=membership_number,
                                            before_date=before_date,
                                            after_date=after_date
                                        )
    
    if success_cart:
        return jsonify({"status": "success", "cart_history_data": cart_history_data})
    else:
        error_message = cart_history_data
        return jsonify({"status": "error", "message": error_message}), 500 

@app.route('/total_spending_filters',methods=["POST"])
def total_spending_filters(before_date=None,after_date=None):
    if 'customer_id' not in session:
        return redirect('/login')
    
    membership_number = session.get('membership_number')
    
    if not membership_number:
        return jsonify({"status": "error", "message": "No membership number in session"}), 401
    
    before_date = request.form.get('spending-date-before')
    after_date = request.form.get('spending-date-after')
    if before_date == "":
        before_date = None
        
    if after_date == "":
        after_date = None
    print(before_date)
    print (after_date)

    total_spending_success, total_spending = getTotalSpending(
                                            customerId=membership_number,
                                            before_date=before_date,
                                            after_date=after_date
                                        )
    print(total_spending)
    
    if total_spending_success:
        return jsonify({"status": "success", "spending_report": total_spending})
    else:
        error_message = total_spending
        return jsonify({"status": "error", "message": error_message}), 500  


@app.route('/search_purchases', methods=['POST'])
def search_purchases():
    """Route for 3.2: Search in Purchase History"""
    if 'customer_id' not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    membership_number = session.get('membership_number')
    data = request.get_json() or {}
    product_name = data.get('product_name')

    if not product_name:
        return jsonify({"status": "error", "message": "Please enter a product name to search."}), 400

    success, result = getItemPurchaseHistory(membership_number, product_name)

    if success:
        return jsonify({"status": "success", "report": result})
    else:
        return jsonify({"status": "error", "message": result}), 404
    
@app.route('/download_purchase_search',methods =['POST'])
def download_purchase_search():
    if 'customer_id' not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    membership_number = session.get('membership_number')
    data = request.get_json() or {};
    format_type = data.get('format')
    product_name = data.get('product_name')

    if not product_name:
        return jsonify({"status": "error", "message": "Product name required"}), 400
    
    success, result = getItemPurchaseHistory(customer_id=membership_number,
                                            product_name=product_name)
    # print(result)
    if not success:
        return jsonify({"status": "error", "message": result}), 404
    
    if format_type == "csv":
        csv_data = Cart_Report.purchase_search_csv(report_data=result,
                                       product_name=product_name,
                                       customerId=membership_number
                                       )
        
        return send_file(
                        io.BytesIO(csv_data),
                        mimetype='text/csv',
                        as_attachment=True,
                        download_name=f'purchase_search_{product_name.replace(" ","_")}_{membership_number}_csv')
    
    elif format_type == "pdf":
        pdf_data = Cart_Report.purchase_search_pdf(report_data=result,
                                       product_name=product_name,
                                       customerId=membership_number)
        return send_file(
            io.BytesIO(pdf_data),
            mimetype='text/pdf',
            as_attachment=True,
             download_name=f'purchase_search_{product_name.replace(" ","_")}_{membership_number}_pdf')
    
@app.route('/download_cart_history',methods =['POST'])
def download_cart_history(before_date=None,after_date=None):
    if 'customer_id' not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    membership_number = session.get('membership_number')
    before_date = request.form.get('date-before')
    after_date = request.form.get('date-after')
    format_type = request.form.get("format")
    if before_date == "":
        before_date = None
        
    if after_date == "":
        after_date = None
    print(before_date)
    print(after_date)

    success_cart, cart_history_data = getCustomerCartHistory(
                                            customerId=membership_number,
                                            before_date=before_date,
                                            after_date=after_date
                                        )
    if not success_cart:
        error_message = cart_history_data
        return jsonify({"status": "error", "message": error_message}), 500 
    
    # print(cart_history_data)
    if format_type == "csv":
        csv_data = Cart_Report.cart_history_csv(report_data=cart_history_data,
                                                customerId=membership_number,
                                                before_date=before_date,
                                                after_date=after_date
                                       )
        # print(csv_data)
        
        return send_file(
                        io.BytesIO(csv_data),
                        mimetype='text/csv',
                        as_attachment=True,
                        download_name=f'cart_history_{membership_number}_csv')
    
    elif format_type == "pdf":
        pdf_data = Cart_Report.cart_history_pdf(report_data=cart_history_data,
                                                customerId=membership_number,
                                                before_date=before_date,
                                                after_date=after_date)
        return send_file(
            io.BytesIO(pdf_data),
            mimetype='text/pdf',
            as_attachment=True,
             download_name=f'cart_history_{membership_number}_pdf')

@app.route('/download_spending_report',methods=['POST'])
def download_spending_report(before_date=None,after_date=None):

    if 'customer_id' not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    membership_number = session.get('membership_number')
    before_date = request.form.get('spending-date-before')
    after_date = request.form.get('spending-date-after')
    format_type = request.form.get("format")
    if before_date == "":
        before_date = None
        
    if after_date == "":
        after_date = None
    print(before_date)
    print(after_date)

    total_spending_success, total_spending = getTotalSpending(
                                            customerId=membership_number,
                                            before_date=before_date,
                                            after_date=after_date
                                        )
    if  not total_spending_success:
        error_message = total_spending
        return jsonify({"status": "error", "message": error_message}), 500  
    if format_type == "csv":
            csv_data = Cart_Report.spending_report_csv( report_data=total_spending,
                                                        customerId=membership_number,
                                                        before_date=before_date,
                                                        after_date=after_date)
            return send_file(
                io.BytesIO(csv_data),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'spending_report_{membership_number}.csv'
            )
    elif format_type == "pdf":
        pdf_data = Cart_Report.spending_report_pdf( report_data=total_spending,
                                                        customerId=membership_number,
                                                        before_date=before_date,
                                                        after_date=after_date)
        return send_file(
                io.BytesIO(pdf_data),
                mimetype='text/pdf',
                as_attachment=True,
                download_name=f'spending_report_{membership_number}.pdf'
            )
        




# -----------------------------------------------------------------------------------

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

@app.route('/inventory-report')
def get_inventory_report():
    format_type = request.args.get('format', 'pdf')
    print(f'fetching inventory report... format: {format_type}')
    file_path = export_inventory_report(format_type)
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({'status': 'error', 'message': 'Failed to generate report'}), 500
    
    mime_type = 'text/csv' if format_type == 'csv' else 'application/pdf'
    return send_file(file_path, mimetype=mime_type, as_attachment=True, 
                     download_name=f'inventory_report.{format_type}')

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

@app.route('/reports/sales.csv')
def download_sales_csv():
    """
    Optional query params: start=YYYY-MM-DD, end=YYYY-MM-DD
    Example: /reports/sales.csv?start=2025-09-01&end=2025-09-30
    """
    start = parse_date_param(request.args.get('start'))
    end = parse_date_param(request.args.get('end'))
    sales = fetch_sales_rows(start_date=start, end_date=end)
    csv_io = generate_csv_bytes(sales)
    # filename with date range
    name = "sales_report"
    if start:
        name += f"_{start.strftime('%Y%m%d')}"
    if end:
        name += f"_{end.strftime('%Y%m%d')}"
    name += ".csv"
    return send_file(csv_io,
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name=name)

@app.route('/reports/sales.pdf')
def download_sales_pdf():
    """
    Optional query params: start=YYYY-MM-DD, end=YYYY-MM-DD
    """
    start = parse_date_param(request.args.get('start'))
    end = parse_date_param(request.args.get('end'))
    sales = fetch_sales_rows(start_date=start, end_date=end)
    pdf_io = generate_pdf_bytes(sales, title="Sales Report")
    name = "sales_report"
    if start:
        name += f"_{start.strftime('%Y%m%d')}"
    if end:
        name += f"_{end.strftime('%Y%m%d')}"
    name += ".pdf"
    return send_file(pdf_io,
                     mimetype='application/pdf',
                     as_attachment=True,
                     download_name=name)


if __name__ == '__main__':
    # app.run(debug=True, use_reloader=False)
    app.run(debug=True, use_reloader=False,host='0.0.0.0',port=5000)