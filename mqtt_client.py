import paho.mqtt.client as mqtt

# Dictionary to store latest readings
data = {
    "Frig1": {"temperature": None, "humidity": None},
    "Frig2": {"temperature": None, "humidity": None}
}

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("Frig1/#")
    client.subscribe("Frig2/#")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    print(f"Topic: {topic}, Message: {payload}")

    if topic.startswith("Frig1"):
        if "temperature" in topic:
            data["Frig1"]["temperature"] = payload
        elif "humidity" in topic:
            data["Frig1"]["humidity"] = payload
    elif topic.startswith("Frig2"):
        if "temperature" in topic:
            data["Frig2"]["temperature"] = payload
        elif "humidity" in topic:
            data["Frig2"]["humidity"] = payload

# Connect to broker
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("172.20.10.12", 1883, 60)
client.loop_start()
