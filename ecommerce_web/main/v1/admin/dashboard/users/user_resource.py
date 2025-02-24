from flask_restful import Resource
from flask import request
from main.database.models import User
from main.extension import db, bcrypt
from main.common.jwt_utils import jwt_required, role_required


class UserListResource(Resource):
    @jwt_required
    @role_required("1")  # Only admin access
    def get(self):
        users = User.query.all()
        return [
            {
                "id": user.id,
                "full_name": user.full_name,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "account_status": user.account_status,
                "profile_pic": user.profile_pic
            }
            for user in users
        ], 200

    @jwt_required
    @role_required("1")
    def post(self):
        data = request.get_json(silent=True) or request.form

        required_fields = ["full_name", "username", "email", "role", "password"]
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return {"message": f"Missing fields: {', '.join(missing_fields)}"}, 400

        if User.query.filter((User.username == data["username"]) | (User.email == data["email"])).first():
            return {"message": "Username or email already exists."}, 400

        password_hash = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

        new_user = User(
            full_name=data["full_name"],
            username=data["username"],
            email=data["email"],
            role=int(data["role"]),
            password_hash=password_hash,
            account_status=data.get("account_status", "1"),
            profile_pic=data.get("profile_pic", "default.png")
        )
        db.session.add(new_user)
        db.session.commit()

        return {
            "message": "User created successfully",
            "user": {
                "id": new_user.id,
                "full_name": new_user.full_name,
                "username": new_user.username,
                "email": new_user.email,
                "role": new_user.role,
                "account_status": new_user.account_status,
                "profile_pic": new_user.profile_pic
            }
        }, 201


class UserResource(Resource):
    @jwt_required
    @role_required("1")
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        return {
            "id": user.id,
            "full_name": user.full_name,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "account_status": user.account_status,
            "profile_pic": user.profile_pic
        }, 200

    @jwt_required
    @role_required("1")
    def put(self, user_id):
        user = User.query.get_or_404(user_id)
        data = request.get_json(silent=True) or request.form

        if data.get("username"):
            user.username = data["username"]
        if data.get("full_name"):
            user.full_name = data["full_name"]
        if data.get("email"):
            user.email = data["email"]
        if data.get("role"):
            user.role = int(data["role"])
        if data.get("account_status"):
            user.account_status = data["account_status"]
        if data.get("profile_pic"):
            user.profile_pic = data["profile_pic"]
        if data.get("password"):
            user.password_hash = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

        db.session.commit()

        return {
            "message": "User updated successfully",
            "user": {
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
    @role_required("1")
    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

        return {"message": "User deleted successfully"}, 200
