# controllers/customer_controller.py
import sqlite3
import RPi.GPIO as GPIO
from time import sleep
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Models.customer import Customer

GREEN_LED = 18
RED_LED = 17
BUZZER = 13

engine = create_engine("sqlite:///sweetcandyco.db")
Session = sessionmaker(bind=engine)

def signal_success():
    GPIO.output(GREEN_LED, GPIO.HIGH)
    sleep(2)
    GPIO.output(GREEN_LED, GPIO.LOW)

def signal_failure():
    GPIO.output(RED_LED, GPIO.HIGH)
    GPIO.output(BUZZER, GPIO.HIGH)
    sleep(2)
    GPIO.output(RED_LED, GPIO.LOW)
    GPIO.output(BUZZER, GPIO.LOW)

def addCustomer(name, email, phone):
    session = Session()
    try:
        customer = Customer.create(session, name, email, phone)
        signal_success()
        return True, "Customer added successfully!"
    except Exception as e:
        session.rollback()
        signal_failure()
        return False, f"Failed to add customer:\n{e}"
    finally:
        session.close()
        GPIO.cleanup()