# controllers/cart_controller.py

from Models.cart import Cart

def addCart(customer_id, total_price, total_reward_points):
    print('Adding cart history...')
    try:
        cart = Cart.create(customer_id, total_price, total_reward_points)
        return True, "Cart added successfully!"
    except Exception as e:
        return False, f"Failed to add cart:\n{e}"