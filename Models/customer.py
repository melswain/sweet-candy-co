# models/customer.py
from sqlalchemy import Column, Integer, String
from .database import Base, execute

class Customer(Base):
    __tablename__ = 'Customer'

    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    phone = Column(String(100), nullable=False, unique=True)
    total_reward_points = Column(Integer, default=0)

    def __repr__(self):
        return f"<Customer(name='{self.name}', email='{self.email}', points={self.total_reward_points})>"
    
    def create(name, email, phone):
        """Insert a new customer into the customer table."""
        query = """
            INSERT INTO customer (name, email, phone)
            VALUES (?, ?, ?)
        """
        try:
            execute(query, (name, email, phone))
            return True, "Customer added successfully."
        except Exception as e:
            return False, f"Error adding customer: {e}"