# services/fan_service.py
import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

Motor1 = 22 # Enable Pin
Motor2 = 27 # Input Pin
GPIO.setup(Motor1,GPIO.OUT)
GPIO.setup(Motor2,GPIO.OUT)

def turnOnFan():
    try:
        GPIO.output(Motor1,GPIO.HIGH)
        GPIO.output(Motor2,GPIO.HIGH)
        print("Motor is on")
        return True,"Fan is ON"
    except Exception as e:
            print(e)
    
    # GPIO.cleanup()

def turnOffFan():
    try:
        GPIO.output(Motor1,GPIO.LOW)
        print("Motor is off")
        return False,"Fan is OFF"
    except Exception as e:
        print (e)
    finally:
        print('Cleaning up...')
        #GPIO.cleanup()

turnOffFan()

def toggle_fan(enabled: bool):
    if enabled:
        success, message = turnOnFan()
    else:
        success, message = turnOffFan()

    print(f"Switch is now {'ON' if enabled else 'OFF'}")
    return success, message