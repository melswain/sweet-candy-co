# services/search_service.py

from Controllers.product_controller import getProductWithId
from Controllers.inventory_controller import searchInventory

def search_item(code, items):
    result, inventory_item_id = searchInventory(code, 1)

    if not inventory_item_id:
        return "error", None, items

    product = getProductWithId(inventory_item_id)
    if not product or not hasattr(product, "productId"):
        return "error", None, items

    unit_price = float(product.price)
    product_id = product.productId

    for item in items:
        if item["id"] == product_id:
            item["quantity"] += 1
            item["total"] = item["quantity"] * unit_price
            return "success", item, items

    new_item = {
        "id": product_id,
        "name": product.name,
        "quantity": 1,
        "unit": unit_price,
        "total": unit_price,
    }
    items.append(new_item)
    return "success", new_item, items