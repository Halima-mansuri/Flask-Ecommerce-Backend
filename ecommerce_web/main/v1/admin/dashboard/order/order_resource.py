from flask_restful import Resource
from flask import request
from main.database.models import Order, Product
from main.extension import db
from datetime import datetime
from main.common.jwt_utils import jwt_required, role_required


class OrderListResource(Resource):
    @jwt_required
    @role_required("1")
    def get(self):
        """Fetch all orders"""
        orders = Order.query.all()
        orders_data = [{
            "id": order.id,
            "customer_id": order.customer_id,
            "product_id": order.product_id,
            "status": order.status,
            "created_at": order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else "Not Available"
        } for order in orders]

        return {"status": "success", "message": "Orders fetched successfully", "data": orders_data}, 200

    @jwt_required
    @role_required("1")
    def post(self):
        """Create a new order (supports JSON and form data)"""
        data = request.get_json(silent=True) or request.form

        customer_id = data.get("customer_id")
        product_id = data.get("product_id")
        status = data.get("status", "Pending")

        if not customer_id or not product_id:
            return {"status": "error", "message": "Customer ID and Product ID are required."}, 400

        # Check product availability
        product = Product.query.filter_by(id=product_id, is_deleted=False).first()
        if not product:
            return {"status": "error", "message": "Product not found or unavailable."}, 404
        if product.quantity <= 0:
            return {"status": "error", "message": "Product out of stock."}, 400

        # Decrement product quantity and create order
        product.quantity -= 1
        new_order = Order(
            customer_id=customer_id,
            product_id=product_id,
            status=status,
            created_at=datetime.utcnow()
        )

        try:
            db.session.add(new_order)
            db.session.commit()
            return {
                "status": "success",
                "message": "Order created successfully",
                "data": {
                    "id": new_order.id,
                    "customer_id": new_order.customer_id,
                    "product_id": new_order.product_id,
                    "status": new_order.status,
                    "created_at": new_order.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            }, 201

        except Exception as e:
            db.session.rollback()
            return {"status": "error", "message": f"Failed to create order: {str(e)}"}, 500


class OrderResource(Resource):
    @jwt_required
    @role_required("1")
    def get(self, order_id):
        """Fetch a specific order by ID"""
        order = Order.query.get_or_404(order_id)
        order_data = {
            "id": order.id,
            "customer_id": order.customer_id,
            "product_id": order.product_id,
            "status": order.status,
            "created_at": order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else "Not Available"
        }
        return {"status": "success", "message": "Order fetched successfully", "data": order_data}, 200

    @jwt_required
    @role_required("1")
    def put(self, order_id):
        """Update order status (supports JSON and form data)"""
        order = Order.query.get_or_404(order_id)
        data = request.get_json(silent=True) or request.form

        if 'status' in data and data['status']:
            order.status = data['status']
        else:
            return {"status": "error", "message": "Status field is required."}, 400

        try:
            db.session.commit()
            return {
                "status": "success",
                "message": "Order updated successfully",
                "data": {
                    "id": order.id,
                    "status": order.status,
                    "created_at": order.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            }, 200
        except Exception as e:
            db.session.rollback()
            return {"status": "error", "message": f"Failed to update order: {str(e)}"}, 500

    @jwt_required
    @role_required("1")
    def delete(self, order_id):
        """Delete an order and restore product quantity"""
        order = Order.query.get_or_404(order_id)
        product = Product.query.filter_by(id=order.product_id, is_deleted=False).first()

        if product:
            product.quantity += 1  # Restore product quantity on order deletion

        try:
            db.session.delete(order)
            db.session.commit()
            return {"status": "success", "message": "Order deleted successfully, product quantity restored."}, 200
        except Exception as e:
            db.session.rollback()
            return {"status": "error", "message": f"Failed to delete order: {str(e)}"}, 500
