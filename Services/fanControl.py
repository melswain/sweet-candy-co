# import RPi.GPIO as GPIO
from time import sleep

# GPIO.setmode(GPIO.BCM)
# GPIO.setwarnings(False)
Motor1 = 22 # Enable Pin
Motor2 = 27 # Input Pin

def turnOnFan():
    print("Turning on a fan...")
    # GPIO.setup(Motor1,GPIO.OUT)
    # GPIO.setup(Motor2,GPIO.OUT)
    try:
        # GPIO.output(Motor1,GPIO.HIGH)
        # GPIO.output(Motor2,GPIO.HIGH)
        print("Motor is on")
    except Exception as e:
        print(e)

def turnOffFan():
    # GPIO.setup(Motor1,GPIO.OUT)
    # GPIO.setup(Motor2,GPIO.OUT)
    try:
        # GPIO.output(Motor1,GPIO.LOW)
        print("Motor is off")
    except Exception as e:
        print (e)
    finally:
        print('Cleaing up...')
        # GPIO.cleanup()