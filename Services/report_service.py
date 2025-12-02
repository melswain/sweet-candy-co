# Services/report_service.py
import io
import csv
from datetime import datetime
from decimal import Decimal
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import PageBreak

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

    # -------------------------
# Receipt-specific helpers
# -------------------------
def fetch_receipts(start_date=None, end_date=None):
    """
    Return a dict (or list) of receipts grouped by cart:
    [
      {
        "cartId": ...,
        "checkoutDate": ...,
        "customerId": ...,
        "cartTotal": ...,
        "items": [
            {"productId":..., "productName":..., "quantity":..., "lineTotal": ...},
            ...
        ]
      },
      ...
    ]
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
            # group by cartId
            receipts = {}
            for r in rows:
                cartId = r[0]
                checkoutDate = r[1]
                customerId = r[2]
                productId = r[3]
                productName = r[4]
                quantity = int(r[5])
                line_total = float(r[6]) if r[6] is not None else 0.0
                cart_total = float(r[7]) if r[7] is not None else 0.0

                if cartId not in receipts:
                    receipts[cartId] = {
                        "cartId": cartId,
                        "checkoutDate": checkoutDate,
                        "customerId": customerId,
                        "cartTotal": cart_total,
                        "items": []
                    }
                receipts[cartId]["items"].append({
                    "productId": productId,
                    "productName": productName,
                    "quantity": quantity,
                    "lineTotal": line_total
                })
            # return a list sorted by checkoutDate/cartId
            receipts_list = list(receipts.values())
            return receipts_list
    except Exception:
        raise

def generate_receipt_csv_bytes(receipts):
    """
    Receipts: list of receipts as returned by fetch_receipts.
    CSV columns:
      Cart ID, Checkout Date, Customer ID, Product ID, Product Name, Quantity, Line Total, Cart Total
    Cart Total will be repeated on each item row (useful for spreadsheet processing).
    """
    mem = io.StringIO()
    writer = csv.writer(mem)
    writer.writerow([
        "Cart ID", "Checkout Date", "Customer ID",
        "Product ID", "Product Name", "Quantity", "Line Total", "Cart Total"
    ])
    for r in receipts:
        dt = r["checkoutDate"]
        dt_str = dt.strftime("%Y-%m-%d %H:%M:%S") if hasattr(dt, "strftime") else str(dt)
        cart_total_s = f"{Decimal(str(r.get('cartTotal', 0))).quantize(Decimal('0.01'))}"
        for item in r["items"]:
            writer.writerow([
                r["cartId"],
                dt_str,
                r["customerId"],
                item["productId"],
                item["productName"],
                item["quantity"],
                f"{Decimal(str(item['lineTotal'])).quantize(Decimal('0.01'))}",
                cart_total_s
            ])
    mem.seek(0)
    b = io.BytesIO()
    b.write(mem.getvalue().encode("utf-8"))
    b.seek(0)
    mem.close()
    return b

def generate_receipt_pdf_bytes(receipts, title="Receipt History"):
    """
    Generate a PDF where each cart is its own receipt block.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 8))

    for idx, r in enumerate(receipts):
        # Receipt header
        dt = r["checkoutDate"]
        dt_str = dt.strftime("%Y-%m-%d %H:%M:%S") if hasattr(dt, "strftime") else str(dt)
        header = f"<b>Receipt - Cart ID:</b> {r['cartId']} &nbsp;&nbsp; <b>Date:</b> {dt_str} &nbsp;&nbsp; <b>Customer:</b> {r.get('customerId', '')}"
        elements.append(Paragraph(header, styles['Normal']))
        elements.append(Spacer(1, 6))

        # Items table for this receipt
        data = [["Product", "Qty", "Line Total"]]
        for item in r["items"]:
            data.append([
                item["productName"],
                str(item["quantity"]),
                f"${Decimal(str(item['lineTotal'])).quantize(Decimal('0.01'))}"
            ])

        # Add total row
        data.append(["", "<b>Total</b>", f"<b>${Decimal(str(r.get('cartTotal', 0))).quantize(Decimal('0.01'))}</b>"])

        table = Table(data, repeatRows=1, hAlign='LEFT', colWidths=[300, 50, 80])
        table_style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F0F0F0")),
            ('GRID', (0,0), (-1,-1), 0.25, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (1,0), (1,-1), 'CENTER'),
            ('ALIGN', (2,0), (2,-1), 'RIGHT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ])
        table.setStyle(table_style)
        elements.append(table)
        elements.append(Spacer(1, 12))

        # Add a page break every N receipts if desired. For clarity, put a pagebreak between receipts.
        if idx < len(receipts) - 1:
            elements.append(PageBreak())

    doc.build(elements)
    buffer.seek(0)
    return buffer


    
