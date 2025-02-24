from flask_restful import Resource
from flask import request
from main.database.models import Product, db
from main.common.jwt_utils import jwt_required, get_jwt_identity, role_required


def parse_request_data():
    """Safely parse data from JSON or form without raising exceptions."""
    if request.content_type and 'application/json' in request.content_type:
        return request.get_json(silent=True) or {}
    return {k: v.strip() if isinstance(v, str) else v for k, v in request.form.items()}


class ProviderAddProductResource(Resource):
    @jwt_required
    @role_required("3")
    def post(self):
        provider_id = get_jwt_identity()
        data = parse_request_data()  # Safe parsing with whitespace handling

        # Validate essential fields
        if not data.get("name") or data.get("price") is None or data.get("quantity") is None:
            return {"status": "error", "message": "Product name, price, and quantity are required"}, 400

        # Validate quantity
        try:
            data["quantity"] = int(str(data["quantity"]).strip())  # Strip whitespace before conversion
            if data["quantity"] < 0:
                raise ValueError
        except (ValueError, TypeError):
            return {"status": "error", "message": "Quantity must be a non-negative integer"}, 400

        # Validate price
        try:
            data["price"] = float(str(data["price"]).strip())  # Strip whitespace before conversion
            if data["price"] < 0:
                raise ValueError
        except (ValueError, TypeError):
            return {"status": "error", "message": "Price must be a non-negative number"}, 400

        # Create product
        new_product = Product(
            name=data["name"],
            description=data.get("description"),
            price=data["price"],
            quantity=data["quantity"],
            provider_id=provider_id
        )

        db.session.add(new_product)
        db.session.commit()

        return {
            "status": "success",
            "message": "Product added successfully",
            "product": {
                "id": new_product.id,
                "name": new_product.name,
                "description": new_product.description,
                "price": new_product.price,
                "quantity": new_product.quantity
            }
        }, 201


class ProviderViewProductsResource(Resource):
    @jwt_required
    @role_required("3")
    def get(self):
        provider_id = get_jwt_identity()
        products = Product.query.filter_by(provider_id=provider_id, is_deleted=False).all()

        if not products:
            return {"status": "error", "message": "No products found."}, 404

        return {
            "status": "success",
            "products": [{
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "quantity": product.quantity
            } for product in products]
        }, 200


class ProviderUpdateProductResource(Resource):
    @jwt_required
    @role_required("3")
    def put(self, product_id):
        provider_id = get_jwt_identity()
        product = Product.query.filter_by(id=product_id, provider_id=provider_id, is_deleted=False).first()

        if not product:
            return {"status": "error", "message": "Product not found or unauthorized"}, 404

        data = parse_request_data()  # Safe parsing

        # Update fields
        product.name = data.get("name", product.name)
        product.description = data.get("description", product.description)

        # Validate price
        if "price" in data:
            try:
                product.price = float(str(data["price"]).strip())
                if product.price < 0:
                    raise ValueError
            except (ValueError, TypeError):
                return {"status": "error", "message": "Price must be a non-negative number"}, 400

        # Validate quantity
        if "quantity" in data:
            try:
                product.quantity = int(str(data["quantity"]).strip())
                if product.quantity < 0:
                    raise ValueError
            except (ValueError, TypeError):
                return {"status": "error", "message": "Quantity must be a non-negative integer"}, 400

        db.session.commit()

        return {
            "status": "success",
            "message": "Product updated successfully",
            "product": {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "quantity": product.quantity
            }
        }, 200


class ProviderDeleteProductResource(Resource):
    @jwt_required
    @role_required("3")
    def delete(self, product_id):
        provider_id = get_jwt_identity()
        product = Product.query.filter_by(id=product_id, provider_id=provider_id, is_deleted=False).first()

        if not product:
            return {"status": "error", "message": "Product not found or unauthorized"}, 404

        # Soft delete
        product.is_deleted = True
        db.session.commit()

        return {"status": "success", "message": "Product soft-deleted successfully"}, 200
