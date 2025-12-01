# models/cart.py
from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base, get_connection, fetchall,fetchone
from datetime import datetime
from types import SimpleNamespace

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
                if cart_id:
                    return True, cart_id
                raise Exception('Failed to obtain last insert id')
        except Exception as e:
            raise

    @staticmethod
    def get_by_customer(customer_id):
        """Return list of carts for a given customer_id as dicts."""
        query = """
            SELECT cartId, customerId, totalCartPrice, totalRewardPoints, checkoutDate
            FROM cart
            WHERE customerId = ?
            ORDER BY checkoutDate DESC
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (customer_id,))
                rows = cursor.fetchall()
                carts = []
                for r in rows:
                    carts.append({
                        'cartId': r[0],
                        'customerId': r[1],
                        'totalCartPrice': float(r[2]) if r[2] is not None else 0.0,
                        'totalRewardPoints': int(r[3]) if r[3] is not None else 0,
                        'checkoutDate': r[4]
                    })
                return carts
        except Exception as e:
            raise

    
    @staticmethod
    def get_customer_cartHistory(customer_id,before_date = None, after_date = None):
    #    ! new Code
        query ="""
                SELECT 
                    ca.cartId,
                    p.name,
                    p.price,
                    ci.quantity,
                    ca.totalCartPrice,
                    ca.checkoutDate
                FROM cart as ca
                JOIN cart_item as ci
                    ON ca.cartId = ci.cartId
                JOIN product as p
                    ON p.productId = ci.productId
                WHERE ca.customerId = ?
               """
        params = [customer_id]
       

        if before_date is not  None:
            query+= " AND ca.checkoutDate <= ?"
            params.append(before_date+" 23:59:59")

        if after_date is not None:

            query+= " AND ca.checkoutDate >= ?"
            params.append(after_date +" 00:00:00")
        
        result = fetchall(query,tuple(params))

        if not result:
            return False, "No cart history found"

        cart_map = {}

        for r in result:
            cartId = r[0]
            name = r[1]
            price = float(r[2])
            quantity = int(r[3])
            totalCartPrice = float(r[4])
            checkoutDate = r[5]

            if cartId not in cart_map:
                cart_map[cartId] = {
                    "cartId": cartId,
                    "totalCartPrice": totalCartPrice,
                    "checkoutDate": checkoutDate,
                    "items": []
                }
            cart_map[cartId]["items"].append({
                "productName": name,
                "quantity": quantity,
                "unitPrice": price,
                "totalProductPrice": round(price * quantity, 2)
            })
        cart_history = list(cart_map.values())

        return True,cart_history

    @staticmethod
    def get_item_purchase_history(customerId,name):
        query = """
                SELECT 
                    ca.checkoutDate,
                    p.price,
                    ci.quantity,
                    ci.totalProductPrice
                FROM cart as ca
                JOIN cart_item as ci
                    ON ca.cartId = ci.cartId
                JOIN product as p
                    ON p.productId = ci.productId
                WHERE ca.customerId = ? AND p.name LIKE ?
                ORDER BY ca.checkoutDate DESC
                """
        params = [customerId, name]
        result = fetchall(query,tuple(params))

        if not result:
            return False, "Product not found in purchase history."
        purchase_history =[];
        total_purchases_count = 0
        
        for r in result:
            date_time = r[0]
            unit_price = float(r[1])
            quantity = int(r[2])
            total_price = float (r[3])

            purchase_history.append({
                "checkoutDate": date_time,
                "quantity": quantity,
                "unitPrice": round(unit_price, 2),
                "totalProductPrice": round(total_price, 2)
            })
            total_purchases_count += quantity

        return True, {
            "product_name": name,
            "total_purchases_count": total_purchases_count,
            "details": purchase_history
        }

    @staticmethod
    def get_total_spending(customerId,before_date=None,after_date=None):
        query = """
                SELECT SUM(ca.totalCartPrice) AS 'TOTAL SPENDING'
                FROM cart AS ca
                WHERE customerId = ?
                """
        params = [customerId]
       
        if before_date is not  None:
            query+= " AND ca.checkoutDate <= ?"
            params.append(before_date+" 23:59:59")

        if after_date is not None:

            query+= " AND ca.checkoutDate >= ?"
            params.append(after_date +" 00:00:00")
        

        result = fetchall(query,tuple(params))
        totalSpending = 0
        print(query)
        print(result)
        if  not result or result is None:
            return False, "Customer has no spending History"

        for r in result:
            if r[0] is not None:
                totalSpending = float (r[0])
            else:
                return False, "Customer has no spending History"
        return True, totalSpending

        

       