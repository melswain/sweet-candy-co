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
from Controllers.product_instance_controller import delete_product_instance

from Services.email_service import send_receipt_email

GST_RATE = Decimal("0.05")
QST_RATE = Decimal("0.09975")

def process_payment(items, card_number, expiry, use_points, membership_number = 0, receipt_email=None):
    # Calculate totals
    subtotal = sum(to_decimal(item.get('total', 0)) for item in items)
    gst = (subtotal * GST_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    qst = (subtotal * QST_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total = (subtotal + gst + qst).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # If no membership provided (guest checkout), skip reward point logic
    if membership_number:
        reward_points = int(subtotal // Decimal('10') * 100)
        success, customer = getCustomerById(membership_number)
        if not success:
            return {"status": 404, "body": {"status": "error", "message": "Customer not found"}}
        email = customer[1][2]
    else:
        reward_points = 0
        customer = None
        # use provided receipt email for guest checkout if present
        email = receipt_email

    # Apply reward points (only for members)
    if use_points and customer:
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
            print("REMOVE INVENTORY: ", removeInventory)
        except Exception as e:
            print("Warning: failed to remove inventory", e)

    # Delete any pending product instances that were scanned (EPCs)
    try:
        # local import to avoid circular imports
        from Services import scan_service
        pending = scan_service.pop_pending_instances()
        # pending is { product_id: [instance_id, ...], ... }
        for product_id, instance_list in pending.items():
            for instance_id in instance_list:
                try:
                    delete_product_instance(instance_id)
                except Exception as e:
                    print(f"Warning: failed to delete product_instance {instance_id}: {e}")
    except Exception as e:
        print("Warning: failed to process pending product instances:", e)

    # Reward points update (only for members)
    if customer:
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

    # Send receipt email if we have an address (member email or guest-supplied)
    if email:
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
    session.clear()

    return {"status": 200, "body": {"status": "success", "message": "Payment processed (simulated)"}}
