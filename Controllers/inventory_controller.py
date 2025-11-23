# controllers/inventory_controller.py

from Models.inventory import Inventory

def removeInventory(product_id, location_id, quantity):
    count = 0

    for _ in range(quantity):
        try:
            Inventory.remove_inventory_item(product_id, location_id)
            count += 1
        except Exception as e:
            return f"Failed to remove product:\n{e}"
    
    return count

def searchInventory(product_id, location_id):
    try:
        item_id = Inventory.search_item(product_id, location_id)
        print("Item: ", item_id[1])
        return True, item_id[1]
    except Exception as e:
        return f"Failed to find product:\n{e}"

def addInventory(product_id, location_id, quantity):
    print(f"Adding Product to Inventory: {product_id}, {location_id}, {quantity}")
    try:
        success,message = Inventory.create(product_id, location_id, quantity)
        if success:
            return True, "Product added successfully to Inventory!"
    except Exception as e:
        return False, f"Failed to add product to Inventory:\n{e}"

def getInventory():
    try:
        success,inventorList = Inventory.getInventory()
        if success:
            return True, inventorList
        else:
            return False,"No Cart History Found"
    except Exception as e:
        return False, f"Error getting cart history: {e}"
