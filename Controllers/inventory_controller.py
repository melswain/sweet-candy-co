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

def searchInventory(product_id, location_id):
    print('Searching for item in inventory...')
    try:
        item_id = Inventory.search_item(product_id, location_id)
        print('Item id: ', item_id[1])
        return True, item_id[1]
    except Exception as e:
        return f"Failed to find product:\n{e}"