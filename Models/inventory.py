# models/inventory.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base, execute
from datetime import datetime

class Inventory(Base):
    __tablename__ = 'inventory'

    inventoryId = Column(Integer, primary_key=True, autoincrement=True)
    productId = Column(Integer, ForeignKey('product.productId'), nullable=False)
    locationId = Column(Integer, ForeignKey('store_location.locationId'), nullable=False)
    quantity = Column(Integer, nullable=False)
    lastUpdated = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="inventory")
    location = relationship("StoreLocation", back_populates="inventory")

    def __repr__(self):
        return f"<Inventory(product_id={self.productId}, location_id={self.locationId}, quantity={self.quantity})>"

    @staticmethod
    def create(product_id, location_id, quantity):
        query = """
            INSERT INTO inventory (productId, locationId, quantity)
            VALUES (?, ?, ?)
        """
        result = execute(query, (product_id, location_id, quantity))
        if result is True:
            return True, "Inventory record created successfully."
        else:
            raise Exception('Error creating inventory record')
        
    @staticmethod
    def remove_inventory_item(product_id, location_id):
        # Get current quantity
        query = """
            SELECT quantity FROM inventory
            WHERE productId = ? AND locationId = ?
        """
        result = execute(query, (product_id, location_id))

        if result:
            quantity = result[0]

            print('Quantity; ', quantity)

            if quantity > 1:
                query = """
                    UPDATE inventory
                    SET quantity = quantity - 1,
                        lastUpdated = CURRENT_TIMESTAMP
                    WHERE productId = ? AND locationId = ?
                """
            else:
                query = """
                    DELETE FROM inventory
                    WHERE productId = ? AND locationId = ?
                """

            print(query)
            affected = execute(query, (product_id, location_id))
            print(affected)
            if affected:
                return True, "Item removed from inventory."
            else:
                raise Exception("Error removing item from inventory")

        else:
            raise Exception("Inventory item not found")