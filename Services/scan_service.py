# services/scan_service.py

from Controllers.product_controller import getProductWithUpc

def normalize_code(code: str):
    # UPC codes sometimes have a leading zero
    if isinstance(code, str) and len(code) == 13 and code.startswith("0"):
        return code[1:]
    return code

def process_scan(code, items):
    code = normalize_code(code)

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