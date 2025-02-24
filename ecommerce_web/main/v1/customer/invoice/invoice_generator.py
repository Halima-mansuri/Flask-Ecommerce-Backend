import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from main.database.models import Order, Product
from datetime import datetime

BASE_INVOICE_DIR = os.path.join(os.getcwd(), "main", "static", "invoices")
os.makedirs(BASE_INVOICE_DIR, exist_ok=True)

def generate_invoice(order_id):
    """Generate a PDF invoice for a given order ID."""
    order = Order.query.get(order_id)
    if not order:
        return {"status": "error", "message": "Order not found.", "file_path": None}

    product = Product.query.get(order.product_id)
    if not product:
        return {"status": "error", "message": "Product not found for this order.", "file_path": None}

    customer_invoice_dir = os.path.join(BASE_INVOICE_DIR, f"customer_{order.customer_id}")
    os.makedirs(customer_invoice_dir, exist_ok=True)

    file_name = f"invoice_{order.id}.pdf"
    file_path = os.path.join(customer_invoice_dir, file_name)

    try:
        c = canvas.Canvas(file_path, pagesize=letter)

        # Handle order date safely
        order_date = "Not Available"
        if hasattr(order, 'created_at') and order.created_at:
            if isinstance(order.created_at, str):
                try:
                    order_date = datetime.strptime(order.created_at, "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d')
                except ValueError:
                    order_date = "Invalid Date Format"
            else:
                order_date = order.created_at.strftime('%Y-%m-%d')

        # Write invoice content
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 750, f"Invoice for Order ID: {order.id}")
        c.setFont("Helvetica", 12)
        c.drawString(100, 730, f"Customer ID: {order.customer_id}")
        c.drawString(100, 710, f"Provider ID: {product.provider_id}")
        c.drawString(100, 690, f"Product: {product.name}")
        c.drawString(100, 670, f"Price: ${product.price:.2f}")
        c.drawString(100, 650, f"Status: {order.status}")
        c.drawString(100, 630, f"Description: {product.description}")
        c.drawString(100, 610, f"Date: {order_date}")

        c.save()

        return {"status": "success", "message": "Invoice generated successfully.", "file_path": file_path}

    except Exception as e:
        return {"status": "error", "message": f"Failed to generate invoice: {str(e)}", "file_path": None}
