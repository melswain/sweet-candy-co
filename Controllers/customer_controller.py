# controllers/customer_controller.py
import sqlite3
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

def addCustomer(name, email, phone):
    print(f"Adding customer: {name}, {email}, {phone}")
    try:
        customer = Customer.create(name, email, phone)
        signal_success()
        return True, "Customer added successfully!"
    except Exception as e:
        signal_failure()
        return False, f"Failed to add customer:\n{e}"
