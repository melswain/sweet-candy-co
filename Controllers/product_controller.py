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
    
def getAllProducts():
    try:
        products = Product.get_all_products()
        return products
    except Exception as e:
        return f"Failed to get products: {e}"
    
def update_product(productId, new_name, new_type, new_price, new_expirationDate, new_manufacturerName, new_upc):
    try:
        products = Product.update_product(productId, new_name, new_type, new_price, new_expirationDate, new_manufacturerName, new_upc)
        return True, products
    except Exception as e:
        return False, f"Failed to update product: {e}"
    
def create_product(name, type_, price, expiration_date, upc, epc, manufacturer_name="Sweet Candy Co", discount=1.00):
    try:
        success, message, id = Product.create(name, type_, price, expiration_date, upc, epc, manufacturer_name, discount)
        return success, message, id
    except Exception as e:
        return False, f"Failed to create product: {e}", 0