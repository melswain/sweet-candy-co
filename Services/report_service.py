# Services/report_service.py
import io
import csv
from datetime import datetime
from decimal import Decimal
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Use existing DB helper you already use elsewhere:
from Models.database import get_connection

def parse_date_param(s):
    """Parse YYYY-MM-DD dates for query params. Return None if invalid/empty."""
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except Exception:
        return None

def fetch_sales_rows(start_date=None, end_date=None):
    """
    Returns list of dicts with columns:
    cartId, checkoutDate, customerId, productId, productName, quantity, totalProductPrice, cartTotal
    start_date/end_date are datetimes (inclusive).
    """
    sql = """
    SELECT
      ca.cartId,
      ca.checkoutDate,
      ca.customerId,
      ci.productId,
      p.name AS productName,
      ci.quantity,
      ci.totalProductPrice,
      ca.totalCartPrice
    FROM cart ca
    JOIN cart_item ci ON ca.cartId = ci.cartId
    JOIN product p ON p.productId = ci.productId
    WHERE 1=1
    """
    params = []
    if start_date:
        sql += " AND ca.checkoutDate >= ?"
        params.append(start_date.strftime("%Y-%m-%d 00:00:00"))
    if end_date:
        sql += " AND ca.checkoutDate <= ?"
        params.append(end_date.strftime("%Y-%m-%d 23:59:59"))
    sql += " ORDER BY ca.checkoutDate ASC, ca.cartId ASC"

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            sales = []
            for r in rows:
                # adapt tuple indices to SQL select order
                sales.append({
                    "cartId": r[0],
                    "checkoutDate": r[1],
                    "customerId": r[2],
                    "productId": r[3],
                    "productName": r[4],
                    "quantity": int(r[5]),
                    "totalProductPrice": float(r[6]) if r[6] is not None else 0.0,
                    "cartTotal": float(r[7]) if r[7] is not None else 0.0
                })
            return sales
    except Exception as e:
        raise

def generate_csv_bytes(sales_rows):
    """
    Return an in-memory BytesIO with CSV content.
    Columns: Cart ID, Checkout Date, Customer ID, Product ID, Product Name,
             Quantity, Line Total, Cart Total
    """
    mem = io.StringIO()
    writer = csv.writer(mem)
    writer.writerow([
        "Cart ID", "Checkout Date", "Customer ID",
        "Product ID", "Product Name", "Quantity",
        "Line Total", "Cart Total"
    ])
    for s in sales_rows:
        writer.writerow([
            s["cartId"],
            s["checkoutDate"],
            s["customerId"],
            s["productId"],
            s["productName"],
            s["quantity"],
            f"{Decimal(str(s['totalProductPrice'])).quantize(Decimal('0.01'))}",
            f"{Decimal(str(s['cartTotal'])).quantize(Decimal('0.01'))}"
        ])
    mem.seek(0)
    # Flask send_file likes BytesIO, so encode to bytes:
    b = io.BytesIO()
    b.write(mem.getvalue().encode("utf-8"))
    b.seek(0)
    mem.close()
    return b

def generate_pdf_bytes(sales_rows, title="Sales Report"):
    """
    Create a simple PDF containing a title, summary and a table of rows.
    Returns BytesIO.
    """
    buffer = io.BytesIO()
    # Use A4 or letter
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=30, bottomMargin=20)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 8))

    # Summary (total sales, number of carts, number of line items)
    total_sales = Decimal('0.00')
    unique_carts = set()
    total_items = 0
    for s in sales_rows:
        total_sales += Decimal(str(s['totalProductPrice']))
        unique_carts.add(s['cartId'])
        total_items += s['quantity']

    summary_text = f"Total sales (sum of line totals): ${total_sales.quantize(Decimal('0.01'))} &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; Total line items: {total_items} &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; Unique carts: {len(unique_carts)}"
    elements.append(Paragraph(summary_text, styles['Normal']))
    elements.append(Spacer(1, 12))

    # Table header and rows
    data = [["Cart ID", "Checkout Date", "Customer ID", "Product ID", "Product Name", "Qty", "Line Total"]]
    for s in sales_rows:
        # friendly date formatting, some DBs already return string
        dt = s["checkoutDate"]
        if hasattr(dt, "strftime"):
            dt_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            dt_str = str(dt)
        data.append([
            s["cartId"],
            dt_str,
            s["customerId"],
            s["productId"],
            s["productName"],
            s["quantity"],
            f"${Decimal(str(s['totalProductPrice'])).quantize(Decimal('0.01'))}"
        ])

    # If table is long, ReportLab will split across pages.
    table = Table(data, repeatRows=1, hAlign='LEFT')
    table_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F0F0F0")),
        ('GRID', (0,0), (-1,-1), 0.25, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (-2,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ])
    table.setStyle(table_style)
    elements.append(table)

    # Build
    doc.build(elements)
    buffer.seek(0)
    return buffer

def fetch_customer_activity_rows(start_date=None, end_date=None):
    """
    Returns a list of dicts with customer activity:
    membershipNumber/customerId, totalPurchases, new/returning, checkoutDate, etc.
    """
    sql = """
    SELECT
        ca.customerId,
        COUNT(DISTINCT ca.cartId) AS totalCarts,
        SUM(ca.totalCartPrice) AS totalSpent,
        MIN(ca.checkoutDate) AS firstPurchase,
        MAX(ca.checkoutDate) AS lastPurchase
    FROM cart ca
    WHERE 1=1
    """
    params = []
    if start_date:
        sql += " AND ca.checkoutDate >= ?"
        params.append(start_date.strftime("%Y-%m-%d 00:00:00"))
    if end_date:
        sql += " AND ca.checkoutDate <= ?"
        params.append(end_date.strftime("%Y-%m-%d 23:59:59"))

    sql += " GROUP BY ca.customerId ORDER BY totalCarts DESC"

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            activity = []
            for r in rows:
                activity.append({
                    "customerId": r[0],
                    "totalCarts": r[1],
                    "totalSpent": float(r[2]) if r[2] is not None else 0.0,
                    "firstPurchase": r[3],
                    "lastPurchase": r[4]
                })
            return activity
    except Exception as e:
        raise


def generate_customer_activity_csv(report, start_date, end_date):
    mem = io.StringIO()
    writer = csv.writer(mem)
    writer.writerow(["Date Range", "Total Customers", "New Customers", "Returning Customers"])

    range_text = f"{start_date} to {end_date}"
    writer.writerow([
        range_text,
        report["total_customers"],
        report["new_customers"],
        report["returning_customers"]
    ])

    b = io.BytesIO()
    b.write(mem.getvalue().encode("utf-8"))
    b.seek(0)
    return b


def generate_customer_activity_pdf(rows, title="Customer Activity Report"):
    """
    Create a PDF for Customer Activity.
    rows: list of dicts with keys:
        customerId, totalCarts, totalSpent, firstPurchase, lastPurchase
    Returns BytesIO.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=30, bottomMargin=20)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 10))

    # Summary
    total_customers = len(rows)
    total_carts = sum(r['totalCarts'] for r in rows)
    total_revenue = sum(Decimal(str(r['totalSpent'])) for r in rows)

    summary_text = (
        f"Total Customers: {total_customers} &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; "
        f"Total Carts: {total_carts} &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; "
        f"Total Revenue: ${total_revenue.quantize(Decimal('0.01'))}"
    )
    elements.append(Paragraph(summary_text, styles['Normal']))
    elements.append(Spacer(1, 12))

    # Table
    data = [["Customer ID", "Total Carts", "Total Spent", "First Purchase", "Last Purchase"]]
    for r in rows:
        first_date = r['firstPurchase'].strftime("%Y-%m-%d %H:%M:%S") if hasattr(r['firstPurchase'], 'strftime') else str(r['firstPurchase'])
        last_date = r['lastPurchase'].strftime("%Y-%m-%d %H:%M:%S") if hasattr(r['lastPurchase'], 'strftime') else str(r['lastPurchase'])
        data.append([
            r['customerId'],
            r['totalCarts'],
            f"${Decimal(str(r['totalSpent'])).quantize(Decimal('0.01'))}",
            first_date,
            last_date
        ])

    table = Table(data, repeatRows=1, hAlign='LEFT')
    table_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F0F0F0")),
        ('GRID', (0,0), (-1,-1), 0.25, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ])
    table.setStyle(table_style)
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer

def fetch_customer_receipts(customer_id, start_date=None, end_date=None):
    sql = """
    SELECT 
        ca.cartId,
        ca.checkoutDate,
        ci.productId,
        p.name AS productName,
        ci.quantity,
        ci.totalProductPrice,
        ca.totalCartPrice
    FROM cart ca
    JOIN cart_item ci ON ca.cartId = ci.cartId
    JOIN product p ON p.productId = ci.productId
    WHERE ca.customerId = ?
    """
    params = [customer_id]

    if start_date:
        sql += " AND ca.checkoutDate >= ?"
        params.append(start_date.strftime("%Y-%m-%d 00:00:00"))

    if end_date:
        sql += " AND ca.checkoutDate <= ?"
        params.append(end_date.strftime("%Y-%m-%d 23:59:59"))

    sql += " ORDER BY ca.checkoutDate DESC, ca.cartId DESC"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()

        receipts = []
        for r in rows:
            receipts.append({
                "cartId": r[0],
                "checkoutDate": r[1],
                "productId": r[2],
                "productName": r[3],
                "quantity": int(r[4]),
                "lineTotal": float(r[5]),
                "cartTotal": float(r[6])
            })
        return receipts

def generate_customer_receipt_history_csv(receipt_rows):
    mem = io.StringIO()
    writer = csv.writer(mem)

    writer.writerow([
        "Cart ID", "Checkout Date", "Product ID",
        "Product Name", "Quantity", "Line Total", "Cart Total"
    ])

    for r in receipt_rows:
        writer.writerow([
            r["cartId"],
            r["checkoutDate"],
            r["productId"],
            r["productName"],
            r["quantity"],
            f"{Decimal(str(r['lineTotal'])).quantize(Decimal('0.01'))}",
            f"{Decimal(str(r['cartTotal'])).quantize(Decimal('0.01'))}"
        ])

    mem.seek(0)
    b = io.BytesIO()
    b.write(mem.getvalue().encode("utf-8"))
    b.seek(0)
    return b

def generate_customer_receipt_history_pdf(receipt_rows, title="Purchase History"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))

    data = [["Cart ID", "Date", "Product", "Qty", "Line Total", "Cart Total"]]

    for r in receipt_rows:
        dt = r["checkoutDate"]
        dt_str = dt.strftime("%Y-%m-%d %H:%M:%S") if hasattr(dt, "strftime") else str(dt)

        data.append([
            r["cartId"],
            dt_str,
            r["productName"],
            r["quantity"],
            f"${Decimal(str(r['lineTotal'])).quantize(Decimal('0.01'))}",
            f"${Decimal(str(r['cartTotal'])).quantize(Decimal('0.01'))}"
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f0f0f0")),
        ('GRID', (0,0), (-1,-1), 0.25, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
    ]))

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer


def fetch_customer_item_search(customer_id, item_name):
    sql = """
    SELECT 
        ca.checkoutDate,
        p.name,
        ci.quantity,
        ci.totalProductPrice
    FROM cart ca
    JOIN cart_item ci ON ca.cartId = ci.cartId
    JOIN product p ON p.productId = ci.productId
    WHERE ca.customerId = ?
      AND p.name LIKE ?
    ORDER BY ca.checkoutDate DESC
    """
    params = [customer_id, f"%{item_name}%"]

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()

        results = []
        for r in rows:
            results.append({
                "checkoutDate": r[0],
                "productName": r[1],
                "quantity": int(r[2]),
                "price": float(r[3])
            })
        return results

def generate_customer_item_search_csv(rows, item_name):
    mem = io.StringIO()
    writer = csv.writer(mem)
    writer.writerow(["Item", item_name])
    writer.writerow(["Purchase Date", "Quantity", "Price"])

    for r in rows:
        writer.writerow([
            r["checkoutDate"],
            r["quantity"],
            f"{Decimal(str(r['price'])).quantize(Decimal('0.01'))}"
        ])

    b = io.BytesIO()
    b.write(mem.getvalue().encode("utf-8"))
    b.seek(0)
    return b

def generate_customer_item_search_pdf(rows, item_name):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"Item Search: {item_name}", styles['Title']))
    elements.append(Spacer(1, 12))

    data = [["Date", "Quantity", "Price"]]

    for r in rows:
        dt = r["checkoutDate"]
        dt_str = dt.strftime("%Y-%m-%d %H:%M:%S") if hasattr(dt, "strftime") else str(dt)

        data.append([
            dt_str,
            r["quantity"],
            f"${Decimal(str(r['price'])).quantize(Decimal('0.01'))}"
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f0f0f0")),
        ('GRID', (0,0), (-1,-1), 0.25, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
    ]))

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

