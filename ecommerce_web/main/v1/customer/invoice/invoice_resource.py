from flask_restful import Resource
from flask import send_file
from main.v1.customer.invoice.invoice_generator import generate_invoice
from main.database.models import Order
from main.common.jwt_utils import jwt_required, get_jwt_identity, role_required
import os


class InvoiceResource(Resource):
    @jwt_required
    @role_required("2")  # Role-based access for customers
    def get(self, order_id):
        identity = get_jwt_identity()

        # Verify order ownership
        order = Order.query.filter_by(id=order_id, customer_id=identity).first()
        if not order:
            return {"status": "error", "message": "Order not found or does not belong to you."}, 404

        # Generate and send invoice
        try:
            result = generate_invoice(order_id)
            file_path = result.get("file_path")
            if result.get("status") != "success" or not file_path or not os.path.exists(file_path):
                return {"status": "error", "message": result.get("message", "Invoice generation failed.")}, 404

            return send_file(file_path, as_attachment=True, download_name=f"invoice_order_{order_id}.pdf")

        except Exception as e:
            return {"status": "error", "message": f"An error occurred: {str(e)}"}, 500
