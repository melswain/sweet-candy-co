# services/scan_service.py

from Controllers.product_controller import getProductWithUpc, getProductWithId
from Controllers.product_instance_controller import get_product_instance_with_epc, delete_product_instance
from Controllers.inventory_controller import removeInventory

# Track scanned EPCs to prevent duplicate processing
scanned_epcs = set()

def is_epc(code):
    code_str = str(code).strip()
    if len(code_str) >= 24 and all(c in '0123456789ABCDEFabcdef' for c in code_str):
        return True
    return False

def process_scan(code, items, location_id=1):
    if is_epc(code):
        return handle_rfid_epc_scan(code, items, location_id)
    
    product = getProductWithUpc(code)
    if not product or not hasattr(product, 'productId'):
        return {
            "status": 404,
            "body": {"status": "error", "message": "Item not found"}
        }

    unit_price = float(product.price)
    product_id = product.productId

    # Check if item already exists
    for item in items:
        if item['id'] == product_id:
            item['quantity'] += 1
            item['total'] = item['quantity'] * unit_price
            return {
                "status": 200,
                "body": {"status": "success", "item": item, "items": items}
            }

    # Add new item
    new_item = {
        'id': product_id,
        'name': product.name,
        'quantity': 1,
        'unit': unit_price,
        'total': unit_price,
    }
    items.append(new_item)

    return {
        "status": 200,
        "body": {"status": "success", "item": new_item, "items": items}
    }

def handle_rfid_epc_scan(epc_code, items, location_id):
    # Check if this EPC was already scanned to prevent duplicates
    if epc_code in scanned_epcs:
        return 200, {"status": "duplicate", "message": "Tag already scanned"}
    
    result, product_instance = get_product_instance_with_epc(epc_code)

    if (result):
        product_instance_id = product_instance[0]
        product_id = product_instance[1]

        delete_result = delete_product_instance(product_instance_id)

        inventory_result = removeInventory(product_id, location_id, 1)

        product = getProductWithId(product_id)

        if not product:
            return 500, {"status": "error", "message": "Product missing for ProductInstance"}

        unit_price = float(product.price)
        product_id = product.productId

        # Mark this EPC as scanned
        scanned_epcs.add(epc_code)

        # Check if item already exists
        for item in items:
            if item['id'] == product_id:
                item['quantity'] += 1
                item['total'] = item['quantity'] * unit_price
                return 200, {"status": "success", "item": item, "items": items}

        # Add new item
        new_item = {
            'id': product_id,
            'name': product.name,
            'quantity': 1,
            'unit': unit_price,
            'total': unit_price,
        }
        items.append(new_item)

        return 200, {"status": "success", "item": new_item, "items": items}
    
    return 500, {"status": "error", "message": "Could not find product with provided EPC"}

def clear_scanned_epcs():
    """Clear the scanned EPCs list (call this when starting a new cart/checkout)"""
    global scanned_epcs
    scanned_epcs.clear()
