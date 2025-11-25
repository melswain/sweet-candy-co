"""epc_reader_service

This service provides a function to start reading EPC tags from a serial
reader and publish them to an MQTT topic. Importing this module should
not block — call `start_epc_reader()` when you want the background thread
to run (or run it from a supervisor process).
"""
import threading
import time
import paho.mqtt.client as mqtt
from flask import jsonify

from Services.scan_service import handle_rfid_epc_scan

try:
    import serial
except Exception:
    serial = None

DEFAULT_SERIAL_PORT = 'COM3'
DEFAULT_BAUD = 9600
DEFAULT_MQTT_BROKER = 'localhost'
DEFAULT_MQTT_PORT = 1883
DEFAULT_TOPIC = 'rfid/scan/store1'


def _reader_loop(port, baud, broker, broker_port, topic, stop_event):
    client = mqtt.Client()
    try:
        client.connect(broker, broker_port)
    except Exception as e:
        print('Failed to connect to MQTT broker in epc reader:', e)
        return

    # If pyserial is not available, just return
    if serial is None:
        print('pyserial not available; epc reader disabled')
        return

    try:
        ser = serial.Serial(port, baud, timeout=1)
    except Exception as e:
        print('Failed to open serial port for EPC reader:', e)
        return

    print('EPC reader started on', port)
    while not stop_event.is_set():
        try:
            raw = ser.readline()
            if not raw:
                time.sleep(0.05)
                continue
            epc = raw.decode(errors='ignore').strip()
            if epc:
                client.publish(topic, epc)
                print(f'Published EPC: {epc}')
        except Exception as e:
            print('Error reading/publishing EPC:', e)
            time.sleep(0.5)


def start_epc_reader(port=DEFAULT_SERIAL_PORT, baud=DEFAULT_BAUD,
                     mqtt_broker=DEFAULT_MQTT_BROKER, mqtt_port=DEFAULT_MQTT_PORT,
                     topic=DEFAULT_TOPIC):
    """Start a background thread that reads EPCs from serial and publishes them.

    Returns a threading.Event that can be set to stop the reader.
    """
    stop_event = threading.Event()
    t = threading.Thread(target=_reader_loop, args=(port, baud, mqtt_broker, mqtt_port, topic, stop_event), daemon=True)
    t.start()
    return stop_event


def handle_rfid(epc, items):
    print(f"RFID EPC received via MQTT: {epc}")

    location_id = 1  # TODO: set per-reader
    status, body = handle_rfid_epc_scan(epc, items, location_id)
    print(f"RFID EPC received: {epc} -> {status} {body['status']}")
    return status, body

    # TODO: update ProductInstance table, mark product as scanned, etc.


if __name__ == '__main__':
    # quick local runner
    ev = start_epc_reader()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ev.set()