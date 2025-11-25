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

DEFAULT_SERIAL_PORT = 'COM4'
DEFAULT_BAUD = 9600
DEFAULT_MQTT_BROKER = 'localhost'
DEFAULT_MQTT_PORT = 1883
DEFAULT_TOPIC = 'rfid/scan/store1'
FALLBACK_BAUDS = [115200, 19200, 38400, 57600, 9600]

def _find_correct_settings(port, timeout=10):
    """Attempt to detect the correct baud rate and line ending by listening for incoming data.
    
    Also tries common initialization sequences to wake up the reader.
    Returns (baud_rate, line_ending) or (DEFAULT_BAUD, b'\n') if detection fails.
    """
    if serial is None:
        print('pyserial not available; cannot auto-detect')
        return DEFAULT_BAUD, b'\n'
    
    print(f'Auto-detecting serial settings on {port}...')
    print('(Scan a tag or send data to the reader now)')
    
    # Common initialization commands to try
    init_commands = [
        b'\r',           # Carriage return (common reset)
        b'\n',           # Newline
        b'AT\r',         # AT command (modem-like)
        b'PING\r',       # Ping
        b'\x00',         # Null byte
    ]
    
    for baud in FALLBACK_BAUDS:
        print(f'  Trying baud {baud}...')
        try:
            ser = serial.Serial(port, baud, timeout=2)
            ser.rtscts = True
            ser.dsrdtr = True
            time.sleep(0.5)  # Let port settle
            
            # Try sending init commands
            for cmd in init_commands:
                try:
                    ser.write(cmd)
                    ser.flush()
                except Exception:
                    pass
            
            start = time.time()
            all_data = b''
            while time.time() - start < timeout:
                # Read raw bytes without waiting for newline
                raw = ser.read(1024)
                if raw:
                    all_data += raw
                    print(f'    Received data at {baud}: {raw}')
                    
                    # Detect line ending in accumulated data
                    if b'\r\n' in all_data:
                        ser.close()
                        return baud, b'\r\n'
                    elif b'\r' in all_data:
                        ser.close()
                        return baud, b'\r'
                    elif b'\n' in all_data:
                        ser.close()
                        return baud, b'\n'
                time.sleep(0.1)
            
            ser.close()
        except Exception as e:
            print(f'    Error: {e}')
    
    print(f'Could not detect settings; using defaults ({DEFAULT_BAUD} baud, newline terminator)')
    return DEFAULT_BAUD, b'\n'


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
        # Enable RTS/DTR handshaking in case reader requires it
        ser.rtscts = True
        ser.dsrdtr = True
    except Exception as e:
        print('Failed to open serial port for EPC reader:', e)
        return

    print('EPC reader started on', port)
    while not stop_event.is_set():
        print('loop')
        try:
            print('try')
            raw = ser.readline()
            print('raw: ', raw)
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

    ser.close()
    print('EPC reader stopped')


def start_epc_reader(port=DEFAULT_SERIAL_PORT, baud=DEFAULT_BAUD,
                     mqtt_broker=DEFAULT_MQTT_BROKER, mqtt_port=DEFAULT_MQTT_PORT,
                     topic=DEFAULT_TOPIC, auto_detect=True):
    """Start a background thread that reads EPCs from serial and publishes them.

    If auto_detect=True, first runs _find_correct_settings() to probe the serial
    port and detect the baud rate and line ending.
    
    Returns a threading.Event that can be set to stop the reader.
    """
    if auto_detect and baud == DEFAULT_BAUD:
        baud, line_ending = _find_correct_settings(port, timeout=10)
        print(f'Auto-detected: {baud} baud, line ending: {line_ending}')
    
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