# models/cart_item.py
from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base, get_connection

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
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (cart_id, product_id, quantity, total_price))
                conn.commit()
                return True, "Cart item added successfully."
        except Exception as e:
            raise

    @staticmethod
    def get_by_cart(cart_id):
        """Return list of cart items for a given cart id, including product info."""
        query = """
            SELECT ci.cartItemId, ci.cartId, ci.productId, p.name, ci.quantity, ci.totalProductPrice
            FROM cart_item ci
            LEFT JOIN product p ON p.productId = ci.productId
            WHERE ci.cartId = ?
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (cart_id,))
                rows = cursor.fetchall()
                items = []
                for r in rows:
                    items.append({
                        'cartItemId': r[0],
                        'cartId': r[1],
                        'productId': r[2],
                        'productName': r[3],
                        'quantity': int(r[4]),
                        'totalProductPrice': float(r[5])
                    })
                return items
        except Exception as e:
            raise