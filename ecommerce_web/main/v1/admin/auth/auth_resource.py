from flask import request, jsonify, current_app
from flask_restful import Resource
import os
from werkzeug.utils import secure_filename
from main.database.models import User, db
from main.extension import bcrypt
from main.common.jwt_utils import generate_token


def save_profile_pic(profile_pic, user_id):
    """Save uploaded profile picture with a unique name."""
    if profile_pic:
        filename = secure_filename(f"{user_id}_{profile_pic.filename}")
        profile_pic_path = os.path.join(current_app.root_path, 'static/profile_pics', filename)
        profile_pic.save(profile_pic_path)
        return f"profile_pics/{filename}"
    return "profile_pics/default.png"


# Admin Registration Resource
class AdminRegistrationResource(Resource):
    def post(self):
        if request.content_type.startswith('multipart/form-data'):
            data = request.form
            profile_pic = request.files.get('profile_pic')
        else:
            data = request.get_json() or {}
            profile_pic = None

        required_fields = ["username", "email", "password", "full_name"]
        if not all(data.get(field) for field in required_fields):
            return {"code": 400, "message": "Missing required fields", "status": 0}, 400

        if User.query.filter_by(email=data["email"]).first():
            return {"code": 400, "message": "Email already registered", "status": 0}, 400

        if User.query.filter_by(username=data["username"]).first():
            return {"code": 400, "message": "Username already taken", "status": 0}, 400

        new_user = User(
            username=data["username"],
            email=data["email"],
            full_name=data["full_name"],
            role="1",  # Assuming 1 = admin
            profile_pic="profile_pics/default.png"
        )
        new_user.set_password(data["password"])

        db.session.add(new_user)
        db.session.commit()

        # Handle profile picture if uploaded
        if profile_pic:
            new_user.profile_pic = save_profile_pic(profile_pic, new_user.id)
            db.session.commit()

        return {
            "code": 201,
            "data": {
                "id": new_user.id,
                "email": new_user.email,
                "full_name": new_user.full_name,
                "profile_pic": new_user.profile_pic,
                "user_type": str(new_user.role),
                "account_status": new_user.account_status
            },
            "message": "Admin registered successfully",
            "status": 1
        }, 201


# Admin Login Resource (Without Refresh Token)
class AdminLoginResource(Resource):
    def post(self):
        if request.content_type.startswith('multipart/form-data'):
            data = request.form
        else:
            data = request.get_json() or {}

        if not data.get("email") or not data.get("password"):
            return {"code": 400, "message": "Email and password are required", "status": 0}, 400

        user = User.query.filter_by(email=data.get("email")).first()

        if not user or not user.check_password(data.get("password")) or user.role != "1":
            return {"code": 401, "message": "Invalid credentials", "status": 0}, 401

        access_token = generate_token(identity=str(user.id), role=user.role, expires_in=3600)

        return {
            "code": 200,
            "data": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "profile_pic": user.profile_pic or "profile_pics/default.png",
                "user_type": user.role,
                "account_status": user.account_status
            },
            "message": "Login successfully",
            "status": 1,
            "token": access_token
        }, 200
