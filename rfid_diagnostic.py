#!/usr/bin/env python3
"""
RFID Reader Diagnostic Tool

Tries all common baud rates and shows raw bytes received,
including initialization attempts.
"""
import time
try:
    import serial
except ImportError:
    print("pyserial not installed. Run: pip install pyserial")
    exit(1)

FALLBACK_BAUDS = [115200, 19200, 38400, 57600, 9600]

def diagnose_port(port, timeout=15):
    print(f"\n{'='*60}")
    print(f"Diagnosing {port}")
    print(f"{'='*60}")
    print("SCAN A TAG NOW or send data to the reader...")
    print()
    
    init_commands = [
        (b'\r', 'CR'),
        (b'\n', 'LF'),
        (b'AT\r', 'AT+CR'),
        (b'PING\r', 'PING+CR'),
        (b'\x00', 'NULL'),
    ]
    
    for baud in FALLBACK_BAUDS:
        print(f"\n--- Baud {baud} ---")
        try:
            ser = serial.Serial(port, baud, timeout=1)
            ser.rtscts = True
            ser.dsrdtr = True
            time.sleep(0.5)
            
            # Send init commands
            print("Sending init commands...")
            for cmd, name in init_commands:
                try:
                    ser.write(cmd)
                    ser.flush()
                    print(f"  Sent: {name}")
                except Exception as e:
                    print(f"  Failed to send {name}: {e}")
            
            print("Listening for data (15s)...")
            start = time.time()
            all_data = b''
            scan_count = 0
            
            while time.time() - start < timeout:
                raw = ser.read(1024)
                if raw:
                    all_data += raw
                    scan_count += 1
                    # Print each chunk as it arrives
                    print(f"  [{scan_count}] Received {len(raw)} bytes: {repr(raw)}")
                    
                    # Show hex and ASCII
                    print(f"       Hex: {raw.hex()}")
                    try:
                        print(f"       ASCII: {raw.decode(errors='replace')}")
                    except:
                        pass
                time.sleep(0.05)
            
            if all_data:
                print(f"\nTotal for {baud}: {len(all_data)} bytes")
                print(f"  Full data: {repr(all_data)}")
            else:
                print(f"No data received at {baud} baud")
            
            ser.close()
        except Exception as e:
            print(f"Error at {baud}: {e}")
    
    print(f"\n{'='*60}")
    print("Diagnosis complete")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    import sys
    port = sys.argv[1] if len(sys.argv) > 1 else 'COM4'
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    diagnose_port(port, timeout)
