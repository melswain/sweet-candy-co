from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

from time import sleep

from Controllers.customer_controller import addCustomer

from Services.fan_service import turnOnFan
from Services.fan_service import turnOffFan

from Services.email_service import sendEmail
from Services.email_service import readEmail

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
    # KISHAAN: add fan state logic function here
    # return f"Switch state updated to {'ON' if enabled else 'OFF'}"

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
