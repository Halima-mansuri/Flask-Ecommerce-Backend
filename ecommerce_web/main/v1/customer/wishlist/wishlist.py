from flask_restful import Resource
from flask import request
from main.database.models import Wishlist, Product
from main.extension import db
from main.common.jwt_utils import jwt_required, get_jwt_identity, role_required


class WishlistResource(Resource):
    @jwt_required
    @role_required("2")  # Role-based access control for customers
    def get(self):
        user_id = get_jwt_identity()
        wishlist_items = Wishlist.query.filter_by(user_id=user_id).all()

        if not wishlist_items:
            return {"status": "error", "message": "No items found in your wishlist."}, 404

        return {
            "status": "success",
            "message": "Wishlist fetched successfully",
            "data": [{
                "product_id": item.product.id,
                "product_name": item.product.name,
                "price": item.product.price,
                "description": item.product.description
            } for item in wishlist_items]
        }, 200

    @jwt_required
    @role_required("2")
    def post(self):
        user_id = get_jwt_identity()

        # Safely handle both JSON and form-data requests
        if request.content_type == 'application/json':
            data = request.get_json(silent=True) or {}
        else:
            data = request.form

        product_id = data.get("product_id")
        if not product_id:
            return {"status": "error", "message": "Product ID is required"}, 400

        # Check if the product exists
        product = Product.query.get(product_id)
        if not product:
            return {"status": "error", "message": "Product not found."}, 404

        # Check if product already in wishlist
        existing_item = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
        if existing_item:
            return {"status": "error", "message": "Product already exists in your wishlist."}, 400

        # Add product to wishlist
        new_wishlist_item = Wishlist(user_id=user_id, product_id=product_id)
        db.session.add(new_wishlist_item)
        db.session.commit()

        return {"status": "success", "message": "Product added to wishlist."}, 201

    @jwt_required
    @role_required("2")
    def delete(self):
        user_id = get_jwt_identity()

        # Handle both JSON and form-data for deletion
        if request.content_type == 'application/json':
            data = request.get_json(silent=True) or {}
        else:
            data = request.form

        product_id = data.get("product_id")
        if not product_id:
            return {"status": "error", "message": "Product ID is required"}, 400

        # Check if the product exists in the wishlist
        wishlist_item = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
        if not wishlist_item:
            return {"status": "error", "message": "Product not found in your wishlist."}, 404

        db.session.delete(wishlist_item)
        db.session.commit()

        return {"status": "success", "message": "Product removed from wishlist."}, 200
