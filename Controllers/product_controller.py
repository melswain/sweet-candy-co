# controllers/product_controller.py

from Models.product import Product


def getProductWithUpc(upc):
    print('Getting product by UPC...')
    try:
        product = Product.get_by_upc(upc)
        return product
    except Exception as e:
        return f"Failed to get product:\n{e}"

def getProductWithEpc(epc):
    print('Getting product by EPC...')
    try:
        product = Product.get_by_epc(epc)
        return product
    except Exception as e:
        return f"Failed to get product:\n{e}"