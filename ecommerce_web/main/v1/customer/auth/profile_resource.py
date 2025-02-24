from flask_restful import Resource
from flask import request, current_app
from main.database.models import User, db
from main.common.jwt_utils import jwt_required, get_jwt_identity, role_required
import os
from werkzeug.utils import secure_filename


def save_profile_pic(profile_pic, user_id):
    """Save uploaded profile picture with a unique name."""
    if profile_pic:
        filename = secure_filename(f"{user_id}_{profile_pic.filename}")
        profile_pic_path = os.path.join(current_app.root_path, 'static/profile_pics', filename)
        profile_pic.save(profile_pic_path)
        return f"profile_pics/{filename}"
    return "profile_pics/default.png"


class CustomerProfileResource(Resource):
    @jwt_required
    @role_required("2")  # Access restricted to customers
    def get(self):
        """Retrieve customer profile details."""
        identity = get_jwt_identity()
        user = User.query.get(int(identity))

        if not user:
            return {
                "code": 404,
                "status": 0,
                "message": "User not found.",
                "data": None
            }, 404

        return {
            "code": 200,
            "status": 1,
            "message": "Profile fetched successfully.",
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
    @role_required("2")
    def put(self):
        """Update customer profile (supports form data, raw JSON, and file handling)."""
        identity = get_jwt_identity()
        user = User.query.get(int(identity))

        if not user:
            return {
                "code": 404,
                "status": 0,
                "message": "User not found.",
                "data": None
            }, 404

        # Handle form data, raw JSON, and file uploads
        if request.content_type.startswith('multipart/form-data'):
            data = request.form
            profile_pic = request.files.get('profile_pic')
        else:
            data = request.get_json(silent=True) or {}
            profile_pic = None

        full_name = data.get("full_name")
        username = data.get("username")
        email = data.get("email")

        updated = False

        if full_name:
            user.full_name = full_name
            updated = True

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

        # Handle profile picture upload
        if profile_pic:
            user.profile_pic = save_profile_pic(profile_pic, user.id)
            updated = True

        if updated:
            try:
                db.session.commit()
                return {
                    "code": 200,
                    "status": 1,
                    "message": "Profile updated successfully.",
                    "data": {
                        "id": user.id,
                        "full_name": user.full_name,
                        "username": user.username,
                        "email": user.email,
                        "profile_pic": user.profile_pic,
                        "role": user.role,
                        "account_status": user.account_status
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
                    "profile_pic": user.profile_pic,
                    "role": user.role,
                    "account_status": user.account_status
                }
            }, 200
