from flask_restful import Resource
from flask import request
from main.database.models import Order, Product, db
from datetime import datetime
from main.v1.customer.invoice.invoice_generator import generate_invoice
from main.common.jwt_utils import jwt_required, get_jwt_identity, role_required
from sqlalchemy.exc import SQLAlchemyError


class PlaceOrderResource(Resource):
    @jwt_required
    @role_required("2")  # Customer role
    def post(self):
        identity = get_jwt_identity()

        #  Handle both JSON and form-data properly
        if request.content_type == 'application/json':
            data = request.get_json(silent=True)  # silent=True prevents exceptions if JSON fails
        else:
            data = request.form

        product_id = data.get("product_id")
        if not product_id:
            return {"status": "error", "message": "Product ID is required."}, 400

        # Check product availability and soft delete
        product = Product.query.filter_by(id=product_id, is_deleted=False).first()
        if not product:
            return {"status": "error", "message": "Product not found or unavailable."}, 404

        if product.quantity <= 0:
            return {"status": "error", "message": "Product out of stock."}, 400

        try:
            #  Create new order
            new_order = Order(
                customer_id=int(identity),
                product_id=product_id,
                created_at=datetime.utcnow()
            )

            #  Decrement product quantity
            product.quantity -= 1

            #  Commit transaction
            db.session.add(new_order)
            db.session.commit()

            #  Generate invoice
            invoice_result = generate_invoice(new_order.id)
            invoice_path = invoice_result.get("file_path") if invoice_result.get("status") == "success" else "Invoice generation failed."

            return {
                "status": "success",
                "message": "Order placed successfully.",
                "data": {
                    "order_id": new_order.id,
                    "customer_id": new_order.customer_id,
                    "product_id": new_order.product_id,
                    "status": new_order.status,
                    "created_at": new_order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    "invoice_path": invoice_path
                }
            }, 201

        except SQLAlchemyError as e:
            db.session.rollback()  #  Rollback in case of error
            return {"status": "error", "message": f"An error occurred: {str(e)}"}, 500
