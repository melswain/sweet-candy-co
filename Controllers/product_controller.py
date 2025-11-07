# controllers/product_controller.py
# import RPi.GPIO as GPIO

from Models.product import Product

def beep():
    print('Beeping')
    # use gpio to beep

def getProductWithUpc(upc):
    print('Getting product by UPC...')
    try:
        product = Product.get_by_upc(upc)
        return product
    except Exception as e:
        return f"Failed to get product:\n{e}"
    finally:
        print('Cleaning up...')
        # GPIO.cleanup()

def getProductWithEpc(epc):
    print('Getting product by EPC...')
    try:
        product = Product.get_by_epc(epc)
        return product
    except Exception as e:
        return f"Failed to get product:\n{e}"
    finally:
        print('Cleaning up...')
        # GPIO.cleanup()