import io
import csv
from datetime import datetime
from decimal import Decimal
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from Models.database import get_connection

@staticmethod
def purchase_search_csv(report_data,product_name,customerId):
    output = io.BytesIO()
    wrapper = io.TextIOWrapper(output,encoding='utf-8-sig',newline = '')

    writer = csv.writer(wrapper)
    writer.writerow(['Purchase History Search Report'])
    writer.writerow(['Customer ID:', customerId])
    writer.writerow(['Product Name:', product_name])
    writer.writerow(['Total Purchases:', report_data.get('total_purchases_count', 0)])
    writer.writerow([])
    writer.writerow(['Date & Time', 'Quantity', 'Total Price'])

    for detail in report_data.get('details', []):
        writer.writerow([
            detail['checkoutDate'],
            detail['quantity'],
            f"${detail['totalProductPrice']:.2f}"
        ])
    wrapper.flush()
    output.seek(0)
    csv_bytes = output.getvalue()
    return csv_bytes

@staticmethod
def purchase_search_pdf(report_data,product_name,customerId):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    title = Paragraph("<b>Purchase History Search Report</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 20))

    summary = Paragraph(
        f"<b>Customer ID:</b> {customerId}<br/>"
        f"<b>Product Name:</b> {product_name}<br/>"
        f"<b>Total Purchases:</b> {report_data.get('total_purchases_count', 0)}",
        styles['Normal']
    )
    elements.append(summary)
    elements.append(Spacer(1, 20))

    table_data = [['Date & Time', 'Quantity', 'Total Price']]
    for detail in report_data.get('details', []):
        table_data.append([
            detail['checkoutDate'],
            str(detail['quantity']),
            f"${detail['totalProductPrice']:.2f}"
        ])

    table = Table(table_data, colWidths=[250, 125, 125])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightpink),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    pdf_bytes = buffer.getvalue()

    return pdf_bytes

# -----------------------------------------------------------------
@staticmethod
def cart_history_csv(report_data,customerId,before_date=None,after_date=None):
    output = io.BytesIO()
    wrapper = io.TextIOWrapper(output,encoding='utf-8-sig',newline='')

    writer = csv.writer(wrapper)
    writer.writerow(['Cart History Report'])
    writer.writerow(['Customer ID:', customerId])
    writer.writerow(['Before_Date: ',before_date or "Unspecified"])
    writer.writerow(['After_Date: ',after_date or "Unspecified"])
    writer.writerow([])
    writer.writerow(['Cart ID', 'Checkout Date', 'Product Name', 'Quantity', 'Total Price', 'Cart Total'])
    
    for cart in report_data:
        first_item = True
        for item in cart.get('items', []):
            if first_item:
                writer.writerow([
                    cart['cartId'],
                    cart['checkoutDate'],
                    item['productName'],
                    item['quantity'],
                    f"${item['totalProductPrice']:.2f}",
                    f"${cart['totalCartPrice']:.2f}"
                ])
                first_item = False
            else:
                writer.writerow([
                    '',
                    '',
                    item['productName'],
                    item['quantity'],
                    f"${item['totalProductPrice']:.2f}",
                    ''
                ])
    wrapper.flush()
    output.seek(0)
    csv_bytes = output.getvalue()
    return csv_bytes

def cart_history_pdf(report_data,customerId,before_date=None,after_date=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    title = Paragraph(f"<b>Cart History Report - Customer {customerId}</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    meta_data = [
        ['Filter Used:', ''],
        ['Before Date:', before_date or "Unspecified"],
        ['After Date:', after_date or "Unspecified"]
    ]
    
    meta_table = Table(meta_data, colWidths=[100, 400])
    meta_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0, 0), (0, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.whitesmoke),
        ('BACKGROUND', (0, 1), (0, -1), colors.lavender),
        ('SPAN', (1, 0), (1, 0)), 
    ]))
    
    elements.append(meta_table)
    elements.append(Spacer(1, 24))
    
    for cart in report_data:
        cart_header = Paragraph(
            f"<b>Cart #{cart['cartId']}</b> - {cart['checkoutDate']} - Total: ${cart['totalCartPrice']:.2f}",
            styles['Heading2']
        )
        elements.append(cart_header)
        elements.append(Spacer(1, 10))
        
        table_data = [['Product Name', 'Quantity', 'Total Price']]
        for item in cart.get('items', []):
            table_data.append([
                item['productName'],
                str(item['quantity']),
                f"${item['totalProductPrice']:.2f}"
            ])
        
        table = Table(table_data, colWidths=[300, 100, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.pink),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))
    doc.build(elements)
    
    pdf_bytes = buffer.getvalue()
    return pdf_bytes

# -------------------------------------------------------------------------------
@staticmethod
def spending_report_csv(report_data,customerId,before_date=None,after_date=None):
    output = io.BytesIO()
    wrapper = (io.TextIOWrapper(output, encoding='utf-8', newline=''))
    
    writer = csv.writer(wrapper)
    writer.writerow(['Total Spending Report'])
    writer.writerow(['Customer ID:', customerId])
    writer.writerow(['Before Date:', before_date or 'All time'])
    writer.writerow(['After Date:', after_date or 'All time'])
    writer.writerow([])
    writer.writerow(['Total Spending:', f'${report_data:.2f}'])

    wrapper.flush()
    output.seek(0)
    csv_bytes = output.getvalue()
    return csv_bytes

@staticmethod
def spending_report_pdf(report_data,customerId,before_date=None,after_date=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    title = Paragraph(f"<b>Total Spending Report</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 20))
    
    info = Paragraph(f"<b>Customer ID:</b> {customerId}<br/>"
                    f"<b>Before Date:</b> {before_date or 'All time'}<br/>"
                    f"<b>After Date:</b> {after_date or 'All time'}<br/><br/>"
                    f"<b>Total Spending:</b> <font color='#d81b60' size='18'>${report_data:.2f}</font>",
                    styles['Normal'])
    elements.append(info)
    
    doc.build(elements)
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    return pdf_bytes

