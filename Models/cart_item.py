# models/cart_item.py
from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base, execute

class CartItem(Base):
    __tablename__ = 'cart_item'

    cartItemId = Column(Integer, primary_key=True, autoincrement=True)
    cartId = Column(Integer, ForeignKey('cart.cartId'), nullable=False)
    productId = Column(Integer, ForeignKey('product.productId'), nullable=False)
    quantity = Column(Integer, nullable=False)
    totalProductPrice = Column(Numeric(10,0), nullable=False)

    # Relationships
    cart = relationship("Cart", back_populates="cart_items")
    product = relationship("Product")

    def __repr__(self):
        return f"<CartItem(id={self.cartItemId}, product_id={self.productId}, quantity={self.quantity})>"

    @staticmethod
    def create(cart_id, product_id, quantity, total_price):
        query = """
            INSERT INTO cart_item (cartId, productId, quantity, totalProductPrice)
            VALUES (?, ?, ?, ?)
        """
        result = execute(query, (cart_id, product_id, quantity, total_price))
        if result is True:
            return True, "Cart item added successfully."
        else:
            raise Exception('Error adding cart item')