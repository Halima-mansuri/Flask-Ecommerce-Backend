from flask_restful import Resource
from flask import request
from main.database.models import Order, Product, db
from datetime import datetime
from main.common.jwt_utils import jwt_required, get_jwt_identity, role_required


def parse_request_data():
    """Safely parse data from JSON or form without raising exceptions."""
    if request.content_type and 'application/json' in request.content_type:
        return request.get_json(silent=True) or {}
    return {k: v.strip() if isinstance(v, str) else v for k, v in request.form.items()}


class ProviderViewOrdersResource(Resource):
    @jwt_required
    @role_required("3")
    def get(self):
        provider_id = get_jwt_identity()
        orders = Order.query.join(Product).filter(Product.provider_id == provider_id).all()

        if not orders:
            return {"status": "error", "message": "No orders found for your products."}, 404

        return {
            "status": "success",
            "orders": [{
                "id": order.id,
                "customer_id": order.customer_id,
                "product_id": order.product_id,
                "status": order.status,
                "created_at": order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else "Not Available"
            } for order in orders]
        }, 200


class ProviderUpdateOrderStatusResource(Resource):
    @jwt_required
    @role_required("3")
    def put(self, order_id):
        provider_id = get_jwt_identity()

        # Validate order_id
        try:
            order_id = int(order_id)
        except (ValueError, TypeError):
            return {"status": "error", "message": "Invalid order ID provided."}, 400

        order = Order.query.join(Product).filter(Order.id == order_id, Product.provider_id == provider_id).first()

        if not order:
            return {"status": "error", "message": "Order not found or unauthorized"}, 404

        data = parse_request_data()  # Safe parsing for JSON and form-data
        status_value = data.get("status")

        # Status validation
        if not status_value:
            return {"status": "error", "message": "Status field is required."}, 400

        if status_value not in ["Pending", "Shipped", "Delivered", "Cancelled"]:
            return {
                "status": "error",
                "message": "Invalid status. Allowed values: Pending, Shipped, Delivered, Cancelled."
            }, 400

        # Update status and timestamp
        order.status = status_value
        if not order.created_at:
            order.created_at = datetime.utcnow()

        db.session.commit()

        return {
            "status": "success",
            "message": "Order status updated successfully",
            "order": {
                "id": order.id,
                "customer_id": order.customer_id,
                "product_id": order.product_id,
                "status": order.status,
                "created_at": order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else "Not Available"
            }
        }, 200
