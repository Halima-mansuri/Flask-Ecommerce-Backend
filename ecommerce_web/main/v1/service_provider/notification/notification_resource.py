from flask_restful import Resource
from flask import request
from main.database.models import Notification, db
from main.common.jwt_utils import jwt_required, get_jwt_identity, role_required


def parse_request_data():
    """Safely parse data from JSON or form without raising exceptions."""
    if request.content_type and 'application/json' in request.content_type:
        return request.get_json(silent=True) or {}
    return {k: v.strip() if isinstance(v, str) else v for k, v in request.form.items()}


class ProviderViewNotificationsResource(Resource):
    @jwt_required
    @role_required("3")
    def get(self):
        provider_id = get_jwt_identity()
        notifications = Notification.query.filter_by(provider_id=provider_id).all()

        if not notifications:
            return {"status": "error", "message": "No notifications found."}, 404

        return {
            "status": "success",
            "notifications": [{
                "id": notification.id,
                "message": notification.message,
                "created_at": notification.created_at.strftime("%Y-%m-%d %H:%M:%S")
            } for notification in notifications]
        }, 200


class ProviderCreateNotificationResource(Resource):
    @jwt_required
    @role_required("3")
    def post(self):
        provider_id = get_jwt_identity()
        data = parse_request_data()  # Safe parsing for JSON and form-data

        # Validation for message field
        message = data.get("message")
        if not message:
            return {"status": "error", "message": "Message is required."}, 400

        # Create and store the notification
        new_notification = Notification(
            provider_id=provider_id,
            message=message
        )

        db.session.add(new_notification)
        db.session.commit()

        return {
            "status": "success",
            "message": "Notification created successfully",
            "notification": {
                "id": new_notification.id,
                "message": new_notification.message,
                "created_at": new_notification.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        }, 201
