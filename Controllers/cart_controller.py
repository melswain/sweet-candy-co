# controllers/cart_controller.py

from Models.cart import Cart

def addCart(customer_id, total_price, total_reward_points):
    print('Adding cart history...')
    try:
        success, cart_id = Cart.create(customer_id, total_price, total_reward_points)
        if success:
            return True, cart_id
        return False, "Failed to create cart"
    except Exception as e:
        return False, f"Failed to add cart:\n{e}"

def getCartsByCustomer(customer_id):
    try:
        carts = Cart.get_by_customer(customer_id)
        return True, carts
    except Exception as e:
        return False, f"Failed to get carts: {e}"