# controllers/customer_controller.py
from Models.database import SessionLocal
from Models.customer import Customer

def add_customer(name, email):
    session = SessionLocal()
    try:
        return Customer.create(session, name, email)
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
        return None
    finally:
        session.close()