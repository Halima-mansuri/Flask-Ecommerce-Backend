from flask import request
from flask_restful import Resource
from main.database.models import User, db
from main.extension import bcrypt
from main.common.jwt_utils import generate_token


# Service Provider Registration Resource
class ProviderRegistrationResource(Resource):
    def post(self):
        # Handle both JSON and form-data requests without error
        if request.content_type == 'application/json':
            data = request.get_json(silent=True) or {}
        else:
            data = request.form

        required_fields = ["username", "email", "password", "full_name"]
        if not all(data.get(field) for field in required_fields):
            return {"code": 400, "message": "Missing required fields", "status": 0}, 400

        # Check if email already exists
        if User.query.filter_by(email=data["email"]).first():
            return {"code": 400, "message": "Email already registered", "status": 0}, 400

        # Create service provider with default profile_pic
        new_user = User(
            username=data["username"],
            email=data["email"],
            full_name=data["full_name"],
            role="3",  # Role for service provider
            profile_pic=data.get("profile_pic", "profile_pics/default.png")
        )
        new_user.set_password(data["password"])

        db.session.add(new_user)
        db.session.commit()

        access_token = generate_token(identity=str(new_user.id), role=new_user.role, expires_in=3600)

        return {
            "code": 201,
            "data": {
                "id": new_user.id,
                "email": new_user.email,
                "full_name": new_user.full_name,
                "profile_pic": new_user.profile_pic,
                "user_type": "3",  # Role as string '3'
                "account_status": new_user.account_status
            },
            "message": "Service provider registered successfully",
            "status": 1,
            "token": access_token
        }, 201


# Service Provider Login Resource (Without Refresh Token)
class ProviderLoginResource(Resource):
    def post(self):
        # Handle both JSON and form-data for login
        if request.content_type == 'application/json':
            data = request.get_json(silent=True) or {}
        else:
            data = request.form

        if not data.get("email") or not data.get("password"):
            return {"code": 400, "message": "Email and password are required", "status": 0}, 400

        user = User.query.filter_by(email=data.get("email")).first()

        # Updated role check to "3" for service providers
        if not user or not user.check_password(data.get("password")) or user.role != "3":
            return {"code": 401, "message": "Invalid credentials", "status": 0}, 401

        access_token = generate_token(identity=str(user.id), role=user.role, expires_in=3600)

        return {
            "code": 200,
            "data": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "profile_pic": user.profile_pic or "profile_pics/default.png",
                "user_type": "3",
                "account_status": user.account_status
            },
            "message": "Login successfully",
            "status": 1,
            "token": access_token
        }, 200
