# controllers/payment_controller.py

from Models.payment import Payment

def addPayment(cart_id, card_number, expiry_date):
    print('Adding payment...')
    try:
        payment = Payment.create(cart_id, card_number, expiry_date)
        return True, "Payment added successfully!"
    except Exception as e:
        return False, f"Failed to add payment:\n{e}"