# controllers/cart_controller.py

from Models.cart import Cart

def addCart(customer_id, total_price, total_reward_points):
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
    
def getCustomerCartHistory(customerId,before_date=None,after_date=None):
    try:
        success, cart_history = Cart.get_customer_cartHistory(customer_id=customerId,before_date=before_date,after_date=after_date)
        if success:
            return True, cart_history
        else:
            return False,"No Cart History Found"
    except Exception as e:
        return False, f"Error getting cart history: {e}"