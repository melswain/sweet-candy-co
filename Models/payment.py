# models/payment.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base, execute
from datetime import datetime

class Payment(Base):
    __tablename__ = 'payment'

    paymentId = Column(Integer, primary_key=True, autoincrement=True)
    cartId = Column(Integer, ForeignKey('cart.cartId'), unique=True)
    cardNumber = Column(String(20), nullable=False)
    expiryDate = Column(String(7), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    cart = relationship("Cart")

    def __repr__(self):
        return f"<Payment(id={self.paymentId}, cart_id={self.cartId})>"

    @staticmethod
    def create(cart_id, card_number, expiry_date):
        query = """
            INSERT INTO payment (cartId, cardNumber, expiryDate)
            VALUES (?, ?, ?)
        """
        result = execute(query, (cart_id, card_number, expiry_date))
        if result is True:
            return True, "Payment processed successfully."
        else:
            raise Exception('Error processing payment')