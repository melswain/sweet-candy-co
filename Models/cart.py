# models/cart.py
from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base, get_connection
from datetime import datetime

class Cart(Base):
    __tablename__ = 'cart'

    cartId = Column(Integer, primary_key=True, autoincrement=True)
    customerId = Column(Integer, ForeignKey('customer.customerId'))
    totalCartPrice = Column(Numeric(10,2), nullable=False)
    totalRewardPoints = Column(Integer, default=0)
    checkoutDate = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="carts")
    cart_items = relationship("CartItem", back_populates="cart")

    def __repr__(self):
        return f"<Cart(id={self.cartId}, customer_id={self.customerId}, total=${self.totalCartPrice})>"

    @staticmethod
    def create(customer_id, total_price, reward_points=0):
        print('Creating cart...')
        query = """
            INSERT INTO cart (customerId, totalCartPrice, totalRewardPoints)
            VALUES (?, ?, ?)
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (customer_id, total_price, reward_points))
                cart_id = cursor.lastrowid
                conn.commit()
                print('LAST INSERTED ID: ', cart_id)
                if cart_id:
                    return True, cart_id
                raise Exception('Failed to obtain last insert id')
        except Exception as e:
            raise