# controllers/product_controller.py

from Models.product import Product

def getProductWithUpc(upc):
    try:
        product = Product.get_by_upc(upc)
        return product
    except Exception as e:
        return f"Failed to get product:\n{e}"

def getProductWithEpc(epc):
    try:
        product = Product.get_by_epc(epc)
        return product
    except Exception as e:
        return f"Failed to get product:\n{e}"

def getProductWithId(id):
    try:
        product = Product.get_by_id(id)
        return product
    except Exception as e:
        return f"Failed to get product:\n{e}"