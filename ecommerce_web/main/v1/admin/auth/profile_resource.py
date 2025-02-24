from flask_restful import Resource
from flask import request
from main.database.models import User, db
from main.common.jwt_utils import jwt_required, get_jwt_identity, role_required


# Admin Profile Resource with PyJWT
class AdminProfileResource(Resource):
    @jwt_required  # Check for valid JWT token
    @role_required("1")  # Ensure only admin can access
    def get(self):
        identity = get_jwt_identity()  # Get user identity from JWT
        user = User.query.get(int(identity))

        if not user:
            return {"code": 404, "message": "User not found", "status": 0}, 404

        return {
            "code": 200,
            "data": {
                "id": user.id,
                "full_name": user.full_name,
                "username": user.username,
                "email": user.email,
                "user_type": user.role,
                "account_status": user.account_status,
                "profile_pic": user.profile_pic
            },
            "message": "Profile fetched successfully",
            "status": 1
        }, 200

    @jwt_required
    @role_required("1")
    def put(self):
        identity = get_jwt_identity()  # Get user identity from JWT
        user = User.query.get(int(identity))

        if not user:
            return {"code": 404, "message": "User not found", "status": 0}, 404

        # Handle both raw JSON and form data
        data = request.get_json(silent=True) or request.form

        # Update user fields if provided
        user.full_name = data.get("full_name", user.full_name)
        user.username = data.get("username", user.username)
        user.email = data.get("email", user.email)
        user.profile_pic = data.get("profile_pic", user.profile_pic)
        user.account_status = data.get("account_status", user.account_status)

        try:
            db.session.commit()
            return {
                "code": 200,
                "data": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "username": user.username,
                    "email": user.email,
                    "user_type": user.role,
                    "account_status": user.account_status,
                    "profile_pic": user.profile_pic
                },
                "message": "Profile updated successfully",
                "status": 1
            }, 200

        except Exception as e:
            db.session.rollback()
            return {"code": 500, "message": f"Failed to update profile: {str(e)}", "status": 0}, 500
