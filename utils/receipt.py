# utils/receipt.py

def receipt_builder(items, subtotal, gst, qst, total, reward_points):
    print(items)
    html = """
        <h2>🧾 Receipt</h2>
        <table border="1" cellspacing="0" cellpadding="6">
        <tr><th>Item</th><th>Qty</th><th>Unit</th><th>Total</th></tr>
    """
    for item in items:
        html += f"""
            <tr>
                <td>{item['name']}</td>
                <td>{item['quantity']}</td>
                <td>${item['unit']:.2f}</td>
                <td>${item['total']:.2f}</td>
            </tr>
        """
    html += f"""
        </table><br>
        <b>Subtotal:</b> ${subtotal:.2f}<br>
        <b>GST:</b> ${gst:.2f}<br>
        <b>QST:</b> ${qst:.2f}<br>
        <b>Total:</b> ${total:.2f}<br>
        <b>Reward Points Earned:</b> {reward_points}<br>
    """
    return html