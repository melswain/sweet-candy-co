# models/product.py
from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base, execute
from datetime import date

class Product(Base):
    __tablename__ = 'product'

    productId = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    price = Column(Numeric(10,0), nullable=False)
    expirationDate = Column(Date, nullable=False)
    discountPercentage = Column(Numeric(3,2), default=1.00)
    manufacturerName = Column(String(100))
    upc = Column(String(50), nullable=False, unique=True)
    epc = Column(String(50), nullable=False)

    # Relationships
    cart_items = relationship("CartItem", back_populates="product")
    inventory = relationship("Inventory", back_populates="product")

    def __repr__(self):
        return f"<Product(name='{self.name}', type='{self.type}', price=${self.price})>"

    @staticmethod
    def create(name, type, price, expiration_date, upc, epc, manufacturer_name="Sweet Candy Co", discount=1.00):
        """Create a new product in the database.
        
        Args:
            name (str): Product name
            type (str): Product type (e.g., 'Chocolate', 'Gummy', etc.)
            price (float): Product price
            expiration_date (date): Expiration date
            upc (str): Universal Product Code
            epc (str): Electronic Product Code
            manufacturer_name (str, optional): Manufacturer name. Defaults to "Sweet Candy Co"
            discount (float, optional): Discount percentage. Defaults to 1.00 (no discount)
        
        Returns:
            tuple: (success (bool), message (str))
        """
        query = """
            INSERT INTO product (name, type, price, expirationDate, manufacturerName, upc, epc, discountPercentage)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            result = execute(query, (
                name, 
                type, 
                price, 
                expiration_date,
                manufacturer_name,
                upc,
                epc,
                discount
            ))
            if result is True:
                return True, "Product created successfully."
            return False, "Failed to create product."
        except Exception as e:
            return False, f"Error creating product: {str(e)}"

    @staticmethod
    def get_by_upc(upc):
        """Find a product by its UPC code.
        
        Args:
            upc (str): Universal Product Code to search for
            
        Returns:
            tuple: Row containing product data or None if not found
        """
        query = "SELECT * FROM product WHERE upc = ?"
        return execute(query, (upc,))

    @staticmethod
    def get_by_type(product_type):
        """Get all products of a specific type.
        
        Args:
            product_type (str): The type of product to search for (e.g., 'Chocolate')
            
        Returns:
            list: List of product rows matching the type
        """
        query = "SELECT * FROM product WHERE type = ?"
        return execute(query, (product_type,))

    @staticmethod
    def update_price(product_id, new_price):
        """Update a product's price.
        
        Args:
            product_id (int): The ID of the product to update
            new_price (float): The new price to set
            
        Returns:
            tuple: (success (bool), message (str))
        """
        query = "UPDATE product SET price = ? WHERE productId = ?"
        result = execute(query, (new_price, product_id))
        if result is True:
            return True, "Price updated successfully."
        return False, "Failed to update price."

    @staticmethod
    def get_expiring_soon(days=30):
        """Get products expiring within the specified number of days.
        
        Args:
            days (int, optional): Number of days to look ahead. Defaults to 30.
            
        Returns:
            list: List of products expiring within the specified timeframe
        """
        query = """
            SELECT * FROM product 
            WHERE date(expirationDate) <= date('now', '+' || ? || ' days')
            ORDER BY expirationDate
        """
        return execute(query, (days,))

    @staticmethod
    def apply_discount(product_id, discount_percentage):
        """Apply a discount to a product.
        
        Args:
            product_id (int): The ID of the product to discount
            discount_percentage (float): Discount as decimal (e.g., 0.90 for 10% off)
            
        Returns:
            tuple: (success (bool), message (str))
        """
        query = "UPDATE product SET discountPercentage = ? WHERE productId = ?"
        result = execute(query, (discount_percentage, product_id))
        if result is True:
            return True, "Discount applied successfully."
        return False, "Failed to apply discount."