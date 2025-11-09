# controllers/cart_item_controller.py

from Models.cart_item import CartItem

def addPayment(cart_id, product_id, quantity, total_price):
    print('Adding payment...')
    try:
        cart_item = CartItem.create(cart_id, product_id, quantity, total_price)
        return True, "Payment added successfully!"
    except Exception as e:
        return False, f"Failed to add payment:\n{e}"