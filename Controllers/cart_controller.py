# controllers/cart_controller.py

from Models.cart import Cart

def addCart(customer_id, total_price, total_reward_points):
    print('Adding cart history...')
    try:
        success, cart_id = Cart.create(customer_id, total_price, total_reward_points)
        print('CART ID: ', cart_id)
        if success:
            return True, cart_id
        return False, "Failed to create cart"
    except Exception as e:
        return False, f"Failed to add cart:\n{e}"