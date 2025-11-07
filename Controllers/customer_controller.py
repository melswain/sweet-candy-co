# controllers/customer_controller.py
import sqlite3
# import RPi.GPIO as GPIO
from time import sleep
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Models.customer import Customer

# --- Mock GPIO mode ---
gpio_mode = "mock"

# Database setup
engine = create_engine("sqlite:///sweetcandyco.db")
Session = sessionmaker(bind=engine)

def setup():
    print("Mock setup: no GPIO available")

def signal_success():
    print("Mock: success signal")  # instead of turning on LEDs

def signal_failure():
    print("Mock: failure signal")  # instead of turning on LEDs/buzzer
GREEN_LED = 18
RED_LED = 17
BUZZER = 13

# GPIO.setmode(GPIO.BCM)
# GPIO.setwarnings(False)
# GPIO.setup(GREEN_LED,GPIO.OUT)
# GPIO.setup(RED_LED,GPIO.OUT)
# GPIO.setup(BUZZER,GPIO.OUT)

# engine = create_engine("sqlite:///sweetcandyco.db")
# Session = sessionmaker(bind=engine)

def setup():
    print('Setting up...')
    # GPIO.setmode(GPIO.BCM)
    # GPIO.setwarnings(False)
    # GPIO.setup(GREEN_LED,GPIO.OUT)
    # GPIO.setup(RED_LED,GPIO.OUT)
    # GPIO.setup(BUZZER,GPIO.OUT)

def signal_success():
    print('Success!')
    # GPIO.setup(GREEN_LED,GPIO.OUT)
    # GPIO.setup(RED_LED,GPIO.OUT)
    # GPIO.setup(BUZZER,GPIO.OUT)
    
    # GPIO.output(GREEN_LED, GPIO.HIGH)
    # sleep(2)
    # GPIO.output(GREEN_LED, GPIO.LOW)

def signal_failure():
    print('Failure!')
    # GPIO.setup(GREEN_LED,GPIO.OUT)
    # GPIO.setup(RED_LED,GPIO.OUT)
    # GPIO.setup(BUZZER,GPIO.OUT)
    
    # GPIO.output(RED_LED, GPIO.HIGH)
    # GPIO.output(BUZZER, GPIO.HIGH)
    # sleep(2)
    # GPIO.output(RED_LED, GPIO.LOW)
    # GPIO.output(BUZZER, GPIO.LOW)

def addCustomer(name, email, phone):
    print(f"Adding customer: {name}, {email}, {phone}")
    try:
        customer = Customer.create(name, email, phone)
        signal_success()
        return True, "Customer added successfully!"
    except Exception as e:
        signal_failure()
        return False, f"Failed to add customer:\n{e}"
