# services/inventory_report_service.py
import os
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from Models.inventory_report import InventoryReport

def export_inventory_report(format_type):
    report_data = InventoryReport.get_inventory_report()

    if (format_type == "csv"):
        return export_inventory_csv(report_data)
    else:
        return export_inventory_pdf(report_data)

from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
import os

def export_inventory_pdf(report_data):
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    pdf_file = os.path.join(downloads_path, "inventory_report.pdf")

    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Inventory Report", styles['Title']))
    elements.append(Spacer(1, 12))

    table_data = [["Product Name", "Product ID", "Available Quantity", "Last Restocked"]]
    for item in report_data[1]:
        table_data.append([
            item.product_name,
            item.product_id,
            item.available_quantity,
            item.last_restocked
        ])

    table = Table(table_data, colWidths=[180, 80, 100, 130])
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F694C1")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#bc1361")),
    ])

    # Apply conditional colors to quantity column (index 2)
    for row_idx, item in enumerate(report_data[1], start=1):
        qty = item.available_quantity
        print(qty)
        if qty > 15:
            style.add('BACKGROUND', (2, row_idx), (2, row_idx), colors.green)
        elif 5 <= qty <= 15:
            style.add('BACKGROUND', (2, row_idx), (2, row_idx), colors.yellow)
        else:  # qty < 5
            style.add('BACKGROUND', (2, row_idx), (2, row_idx), colors.red)

    table.setStyle(style)

    elements.append(table)
    doc.build(elements)

    print(f"PDF saved to {pdf_file}")
    return pdf_file

def export_inventory_csv(report_data):
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    csv_file = os.path.join(downloads_path, "inventory_report.csv")
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Product ID", "Product Name", "Quantity", "Last Restock"])
        for item in report_data[1]:
            writer.writerow([item.product_id, item.product_name, item.available_quantity, item.last_restocked])
    
    print(f"CSV saved to {csv_file}")
    return csv_file