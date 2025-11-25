# models/product_instance.py
from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base, execute, fetchone, fetchall
from types import SimpleNamespace
from datetime import date


class ProductInstance(Base):
    __tablename__ = 'productInstance'

    productInstanceId = Column(Integer, primary_key=True, autoincrement=True)
    productId = Column(Integer, nullable=False)
    epcCode = Column(String(50), nullable=False, unique=True)

    @staticmethod
    def create(productId, epcCode):
        
        query = """
            INSERT INTO productInstance (productId, epcCode)
            VALUES (?, ?)
        """
        try:
            result = execute(query, (productId, epcCode))

            if result is True:
                query = "SELECT COUNT(*) FROM productInstance";
                result = fetchone(query)
                return True, "Product instance created successfully.", result[0]
            return False, "Failed to create product instance.", 0
        except Exception as e:
            return False, f"Error creating product instance: {str(e)}"

    @staticmethod
    def get_by_epc(epc):
        query = "SELECT productInstanceId, productId, epcCode FROM productInstance WHERE epcCode = ?"
        
        product_instance = fetchone(query, (epc,))
        if not product_instance:
            return False, None
        
        return True, product_instance
    
    @staticmethod
    def get_by_id(id):
        query = "SELECT productInstanceId, productId, epcCode FROM productInstance WHERE productInstanceId = ? "
        product_instance = fetchone(query, (id,))
        if not product_instance:
            return False, None
        
        return True, product_instance
    
    @staticmethod
    def remove_instance(product_instance_id):
        query = "DELETE FROM ProductInstance WHERE productInstanceId = ?"
        result = execute(query, (product_instance_id,))
        return result
