# utils/finance.py
from decimal import Decimal

def to_decimal(v):
    return v if isinstance(v, Decimal) else Decimal(str(v))