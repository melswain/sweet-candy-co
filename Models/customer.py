# models/customer.py
from sqlalchemy import Column, Integer, String
from .database import Base, execute

class Customer(Base):
    __tablename__ = 'customer'

    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    phone = Column(String(100), nullable=False, unique=True)
    total_reward_points = Column(Integer, default=0)

    def __repr__(self):
        return f"<Customer(name='{self.name}', email='{self.email}', points={self.total_reward_points})>"

    @staticmethod        
    def create(name, email, phone):
        print('Creating customer...')
        query = """
            INSERT INTO customer (name, email, phone)
            VALUES (?, ?, ?)
        """
        result = execute(query, (name, email, phone))
        if result is True:
            print('Customer added successfully.')
            return True, "Customer added successfully."
        else:
            print('Error adding customer.')
            raise Exception('Error adding customer')