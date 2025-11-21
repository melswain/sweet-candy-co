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

def addRewardPoints(customer_id, reward_points):
    print('Adding reward points...')
    try:
        customer = Customer.addRewardPoints(customer_id, reward_points)
        return True, "Successfully added reward points!"
    except Exception as e:
        return False, "Failed to add reward points: {e}"
    
# def verifyMembershipNumber(customer_id):
#     print('Verifying membership...')
#     try:
#         customer = Customer.getCustomer(customer_id).first()
#         if customer:
#             return True, "Customer exists."
#         else:
#             return False, "Customer not found."
#     except Exception as e:
#         return False, f"Error verifying membership: {e}"
    
def getCustomerById(customer_id):
    try:
        customer = Customer.getCustomerById(customer_id)
        if customer:
            print(customer)
            return True, customer
        else:
            return False, "Customer not found."
    except Exception as e:
        return False, f"Error getting customer: {e}"
    
def subtractRewardPoints(customer_id, points):
    try:
        customer = Customer.subtractRewardPoints(customer_id, points)
        if customer:
            return True
        else:
            return False, "Could not subtract points from customer."
    except Exception as e:
        return False, f"Error subtracting points: {e}"
    
def customer_login(customer_id, password):
    try:
        print('made it here.')
        customer = Customer.login_customer(customer_id, password)
        if customer:
            return True, None
        else:
            print('Error logging in. Username and/or password could be incorrect.')
            return False, f"Error logging in. Username and/or password could be incorrect."
    except Exception as e:
        return False, f"Error logging in: {e}"