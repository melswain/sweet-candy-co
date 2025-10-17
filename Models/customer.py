# models/customer.py
from sqlalchemy import Column, Integer, String
from .database import Base, execute
from sqlalchemy.orm import Session

class Customer(Base):
    __tablename__ = 'Customer'

    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    phone = Column(String(100), nullable=False, unique=True)
    total_reward_points = Column(Integer, default=0)

    def __repr__(self):
        return f"<Customer(name='{self.name}', email='{self.email}', points={self.total_reward_points})>"
    
    @staticmethod
    def create(session: Session, name: str, email:str , phone: str):
        """Insert a new customer into the customer table (using SQLALchemy ORM)."""
        try:
            new_customer = Customer(name=name, email=email, phone=phone)
            session.add(new_customer)
            session.commit()
            return True, "Customer added successfully."
        except Exception as e:
            session.rollback()
            return False, f"Error adding customer: {e}"