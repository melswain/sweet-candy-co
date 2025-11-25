# models/inventory.py

from .database import Base, execute, fetchall
from types import SimpleNamespace


class Inventory(Base):
    @staticmethod
    def create_inventory_report(product_name, product_id, available_quantity, last_restocked):
        query = """
            INSERT INTO inventoryReport (productName, productId, availableQuantity, lastRestocked)
            VALUES (?, ?, ?, ?)
        """
        result = execute(query, (product_name, product_id, available_quantity, last_restocked))
        if result is True:
            return True, "Inventory report record created successfully."
        else:
            raise Exception('Error creating inventory report record')
    
    @staticmethod
    def get_inventory_report():
        query = """
                SELECT * FROM inventoryReport
                """
        rows = fetchall(query)
        if rows is False or rows is None:
            return False, "Failed retrieve inventory reports."
        keys = ['inventory_report_id','product_name','product_id','available_quantity','last_restocked']
        inventory_list = [SimpleNamespace(**{k: row[i] for i,k in enumerate(keys)}) for row in rows]
        return True,inventory_list