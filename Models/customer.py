# models/customer.py
from sqlalchemy import Column, Integer, String
from .db import Base

class Customer(Base):
    __tablename__ = 'Customer'

    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    # should we add date of birth?
    total_reward_points = Column(Integer, default=0)

    def __repr__(self):
        return f"<Customer(name='{self.name}', email='{self.email}', points={self.total_reward_points})>"
    
    @classmethod
    def create(cls, session, name, email):
        customer = cls(
            name=name,
            email=email
        )
        session.add(customer)
        session.commit()
        return customer
