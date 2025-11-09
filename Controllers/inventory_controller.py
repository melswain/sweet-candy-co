# controllers/inventory_controller.py

from Models.inventory import Inventory

def removeInventory(product_id, location_id, quantity):
    print('Removing inventory item...')
    count = 0

    for _ in range(quantity):
        try:
            Inventory.remove_inventory_item(product_id, location_id)
            count += 1
        except Exception as e:
            return f"Failed to remove product:\n{e}"
    
    return count