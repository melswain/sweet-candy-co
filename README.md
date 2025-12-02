# Sweet Candy Co.

This project is a Raspberry Pi-based IoT system for managing customer data in a smart store. It is a candy store called Sweet Candy Co. It uses Python, MySQL, and GPIO hardware feedback (LEDs, buzzers) to provide real-time interaction and alerts.

## Features

- Add new customers to the MySQL database
- Trigger hardware feedback (blue LED for success, red LED + buzzer for failure)
- MVC architecture
- Environment-based configuration

## Dependencies

Install all required packages using pip:

```bash
pip install flask sqlalchemy pymysql python-dotenv RPi.GPIO pyseria paho-mqtt reportlab werkzeug
```

## Configuration

Make sure to create a .env file that contains the necessary information.

- FLASK_SECRET_KEY

## Using a Flask Server

1. Make sure Flask in installed: ```pip install flask```
2. Set up the .env file by installing python-dotenv ```pip install python-dotenv```
3. Include the Flask secret key in the .env as FLASK_SECRET_KEY
4. Access the local application using ```python app.py``` in the terminal when in sweet-candy-co
5. Visit http://127.0.0.1:5000 to view the web app

## Configuring MQTT for RFID

### Linux

```
export RFID_SERIAL_PORT=/dev/ttyUSB0
export RFID_BAUD=9600
export RFID_SERVER_URL=http://127.0.0.1:5000/scan
python rfid_service.py
```

### PowerShell

set env vars for the current PowerShell session
$env:RFID_SERIAL_PORT = 'COM4'            # change to your port
$env:RFID_BAUD = '9600'                  # change if needed
$env:RFID_SERVER_URL = 'http://127.0.0.1:5000/scan'

optional:
$env:RFID_DEVICE_TOKEN = 'my-secret-token'  

run bridge
python .\rfid_service.py