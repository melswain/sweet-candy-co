# services/payment_service.py
from flask import session
from decimal import Decimal, ROUND_HALF_UP
from utils.finance import to_decimal
from utils.receipt import receipt_builder

from Controllers.customer_controller import addRewardPoints, getCustomerById, subtractRewardPoints
from Controllers.cart_controller import addCart
from Controllers.cart_item_controller import addPayment as addCartItem
from Controllers.payment_controller import addPayment
from Controllers.inventory_controller import removeInventory

from Services.email_service import send_receipt_email

GST_RATE = Decimal("0.05")
QST_RATE = Decimal("0.09975")

def process_payment(items, membership_number, card_number, expiry, use_points):
    # Calculate totals
    subtotal = sum(to_decimal(item.get('total', 0)) for item in items)
    gst = (subtotal * GST_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    qst = (subtotal * QST_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total = (subtotal + gst + qst).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    reward_points = int(subtotal // Decimal('10') * 100)

    success, customer = getCustomerById(membership_number)
    if not success:
        return {"status": 404, "body": {"status": "error", "message": "Customer not found"}}
    email = customer[1][2]

    # Apply reward points
    if use_points:
        points = customer[1][1]
        discount_dollars = Decimal(points // 100)
        if discount_dollars > 0:
            total -= discount_dollars
            points_used = int(discount_dollars * 100)
            subtractRewardPoints(membership_number, points_used)

    # Inventory update
    for item in items:
        try:
            removeInventory(item["id"], 1, item["quantity"])
        except Exception as e:
            print("Warning: failed to remove inventory", e)

    # Reward points update
    customer_success, customer_result = addRewardPoints(membership_number, reward_points)
    if not customer_success:
        return {"status": 400, "body": {"status": "error", "message": customer_result}}

    # Cart creation
    cart_success, cart_result = addCart(membership_number, float(total), reward_points)
    if not cart_success:
        return {"status": 400, "body": {"status": "error", "message": cart_result}}
    cart_id = cart_result

    # Cart items
    for item in items:
        cart_item_success, cart_item_message = addCartItem(
            cart_id=cart_id,
            product_id=item['id'],
            quantity=item['quantity'],
            total_price=float(item['total'])
        )
        if not cart_item_success:
            return {"status": 400, "body": {"status": "error", "message": cart_item_message}}

    # Payment record
    payment_success, payment_message = addPayment(cart_id, card_number, expiry)

    # Receipt
    receipt_html = receipt_builder(items, subtotal, gst, qst, total, reward_points)

    try:
        send_receipt_email(
            receiver_email=email,
            subject="Your Purchase Receipt",
            html_content=receipt_html
        )
    except Exception as e:
        return {"status": 500, "body": {"status": "warning", "message": "Payment processed but email failed", "error": str(e)}}

    # Cleanup
    items.clear()
    session.pop('membership_number', None)
    session.pop('usePoints', None)

    return {"status": 200, "body": {"status": "success", "message": "Payment processed (simulated)"}}
