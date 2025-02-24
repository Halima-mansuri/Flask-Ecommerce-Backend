from flask_restful import Resource
from flask import request
from main.database.models import User, db
from main.common.jwt_utils import jwt_required, get_jwt_identity, role_required


# Service Provider Profile Resource
class ProviderProfileResource(Resource):
    @jwt_required  # Check for valid JWT token
    @role_required("3")  # Ensure only service providers can access
    def get(self):
        """Retrieve service provider profile details."""
        identity = get_jwt_identity()
        user = User.query.get(int(identity))

        if not user:
            return {
                "code": 404,
                "status": 0,
                "message": "User not found",
                "data": None
            }, 404

        return {
            "code": 200,
            "status": 1,
            "message": "Profile fetched successfully",
            "data": {
                "id": user.id,
                "full_name": user.full_name,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "account_status": user.account_status,
                "profile_pic": user.profile_pic
            }
        }, 200

    @jwt_required
    @role_required("3")
    def put(self):
        """Update service provider profile (supports form data and raw JSON)."""
        identity = get_jwt_identity()
        user = User.query.get(int(identity))

        if not user:
            return {
                "code": 404,
                "status": 0,
                "message": "User not found",
                "data": None
            }, 404

        # Handle both raw JSON and form data
        data = request.get_json(silent=True) or request.form

        full_name = data.get("full_name")
        username = data.get("username")
        email = data.get("email")
        profile_pic = data.get("profile_pic")
        account_status = data.get("account_status")

        updated = False

        # Update full_name if provided
        if full_name:
            user.full_name = full_name
            updated = True

        # Update username if provided and unique
        if username and username != user.username:
            if User.query.filter(User.username == username, User.id != user.id).first():
                return {
                    "code": 400,
                    "status": 0,
                    "message": "Username already taken by another user.",
                    "data": None
                }, 400
            user.username = username
            updated = True

        # Update email if provided and unique
        if email and email != user.email:
            if User.query.filter(User.email == email, User.id != user.id).first():
                return {
                    "code": 400,
                    "status": 0,
                    "message": "Email already in use by another user.",
                    "data": None
                }, 400
            user.email = email
            updated = True

        # Update profile picture if provided
        if profile_pic:
            user.profile_pic = profile_pic
            updated = True

        # Update account status if provided
        if account_status:
            user.account_status = account_status
            updated = True

        if updated:
            try:
                db.session.commit()
                return {
                    "code": 200,
                    "status": 1,
                    "message": "Profile updated successfully",
                    "data": {
                        "id": user.id,
                        "full_name": user.full_name,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                        "account_status": user.account_status,
                        "profile_pic": user.profile_pic
                    }
                }, 200
            except Exception as e:
                db.session.rollback()
                return {
                    "code": 500,
                    "status": 0,
                    "message": f"Failed to update profile: {str(e)}",
                    "data": None
                }, 500
        else:
            return {
                "code": 200,
                "status": 1,
                "message": "No changes provided for update.",
                "data": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "account_status": user.account_status,
                    "profile_pic": user.profile_pic
                }
            }, 200
