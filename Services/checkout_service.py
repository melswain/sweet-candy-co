# services/checkout_service.py
from decimal import Decimal, ROUND_HALF_UP

GST_RATE = Decimal("0.05")
QST_RATE = Decimal("0.09975")

def to_decimal(v):
    return v if isinstance(v, Decimal) else Decimal(str(v))

def calculate_checkout(items):
    subtotal = Decimal('0.00') if not items else sum(
        to_decimal(item.get('total', 0)) for item in items
    )
    gst = (subtotal * GST_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    qst = (subtotal * QST_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total = (subtotal + gst + qst).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    reward_points = int(subtotal // Decimal('10') * 100)

    return {
        "items": items,
        "subtotal": subtotal,
        "gst": gst,
        "qst": qst,
        "total": total,
        "reward_points": reward_points
    }