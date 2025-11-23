# services/product_service.py
from Controllers.inventory_controller import addInventory
from Controllers.product_controller import update_product, create_product
from Controllers import product_controller

def update_product(data):
    try:
        result, message = product_controller.update_product(
            productId=data.get("productId"),
            new_name=data.get("name"),
            new_type=data.get("type"),
            new_price=data.get("price"),
            new_expirationDate=data.get("expirationDate"),
            new_manufacturerName=data.get("manufacturerName"),
            new_upc=data.get("upc"),
            new_epc=data.get("epc")
        )
        return {"success": result, "message": message}
    except Exception as e:
        return {"success": False, "message": str(e)}

def add_product(data):
    try:
        success, message, newProductId = create_product(
            name=data.get("name"),
            type_=data.get("type"),
            price=data.get("price"),
            expiration_date=data.get("expirationDate"),
            manufacturer_name=data.get("manufacturerName"),
            upc=data.get("upc"),
            epc=data.get("epc")
        )
        
        if success:
            return {"success": True, "message": message, "id": newProductId}

    except Exception as e:
        return {"success": False, "message": str(e)}