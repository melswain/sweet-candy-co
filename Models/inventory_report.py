from .database import fetchall
from types import SimpleNamespace

class InventoryReport():
    
    @staticmethod
    def get_inventory_report():
        query = """
                SELECT 
                    p.productId,
                    p.name AS productName,
                    i.quantity AS inventoryQuantity,
                    i.lastUpdated AS lastRestock
                FROM 
                    product p
                JOIN 
                    inventory i ON p.productId = i.productId
                WHERE 
                    i.locationId = 1;
                """
        rows = fetchall(query)
        if rows is False or rows is None:
            return False, "Failed retrieve inventory reports."
        keys = ['product_id','product_name','available_quantity','last_restocked']
        inventory_list = [SimpleNamespace(**{k: row[i] for i,k in enumerate(keys)}) for row in rows]
        return True, inventory_list