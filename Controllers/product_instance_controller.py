# controllers/product_instance_controller.py

from Models.product_instance import ProductInstance

def get_product_instance_with_epc(epc):
    try:
        result, product = ProductInstance.get_by_epc(epc)
        if (result):
            return result, product
        else:
            return result, "Failed to get product instance with its ID."
    except Exception as e:
        return f"Failed to get product:\n{e}"

def get_product_instance_with_id(id):
    try:
        result, product = ProductInstance.get_by_id(id)
        if (result):
            return result, product
        else:
            return result, "Failed to get product instance with its ID."
    except Exception as e:
        return result, f"Failed to get product:\n{e}"

def create_product(productId, epcCode):
    try:
        success, message, id = ProductInstance.create(productId, epcCode)
        return success, message, id
    except Exception as e:
        return False, f"Failed to create product: {e}", 0
    
def delete_product_instance(product_instance_id):
    try:
        result = ProductInstance.remove_instance(product_instance_id)
        return result
    except Exception as e:
        return False, f"Failed to remove product: {e}"