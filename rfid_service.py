"""
Simple RFID serial bridge.

Run this script on the checkout terminal that has a USB/serial RFID reader attached.
It reads tag strings from the serial port and POSTs them to the Flask `/scan` endpoint.

Configure via environment variables:
 - RFID_SERIAL_PORT (e.g., COM3 or /dev/ttyUSB0)
 - RFID_BAUD (e.g., 9600)
 - RFID_SERVER_URL (default: http://127.0.0.1:5000/scan)
 - RFID_DEVICE_TOKEN (optional) -- sent as X-Device-Token header for basic auth

"""
import os
import time
try:
    import serial
except Exception:
    serial = None
import requests

SERIAL_PORT = os.getenv('RFID_SERIAL_PORT', '')
BAUD = int(os.getenv('RFID_BAUD', '9600'))
SERVER_URL = os.getenv('RFID_SERVER_URL', 'http://127.0.0.1:5000/scan')
DEVICE_TOKEN = os.getenv('RFID_DEVICE_TOKEN')

def read_loop():
    if serial is None:
        print('pyserial not installed. Install with: pip install pyserial')
        return
    if not SERIAL_PORT:
        print('RFID_SERIAL_PORT not set. Export RFID_SERIAL_PORT=COM3 (Windows) or /dev/ttyUSB0')
        return

    print(f'Opening serial port {SERIAL_PORT} @ {BAUD} baud, sending to {SERVER_URL}')
    with serial.Serial(SERIAL_PORT, BAUD, timeout=1) as ser:
        buffer = ''
        while True:
            try:
                data = ser.read(ser.in_waiting or 1).decode(errors='ignore')
            except Exception as e:
                print('Serial read error:', e)
                time.sleep(1)
                continue
            if not data:
                time.sleep(0.01)
                continue
            buffer += data
            # some readers send newline after tag
            if '\n' in buffer or '\r' in buffer:
                tag = buffer.strip()
                buffer = ''
                if tag:
                    headers = {'Content-Type': 'application/json'}
                    if DEVICE_TOKEN:
                        headers['X-Device-Token'] = DEVICE_TOKEN
                    try:
                        resp = requests.post(SERVER_URL, json={'code': tag}, headers=headers, timeout=3)
                        print('Sent', tag, '->', resp.status_code, resp.text)
                    except Exception as e:
                        print('Error sending tag', e)

if __name__ == '__main__':
    read_loop()