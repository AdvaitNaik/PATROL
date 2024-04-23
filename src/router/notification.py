from flask import Blueprint, Response, request, jsonify
from src.database.model import BroadcastMessage, User
from src.database.db import db
from src.utils.firebase import send_notification, check_role_authorization, Roles
from datetime import datetime

message_bp = Blueprint('message', __name__)


# ------------------------------ Util Methods ------------------------------ #
def get_user_id_by_email(email):
    user = User.query.filter_by(email=email).first()
    return user.user_id if user else None


# ------------------------------ /message/healthCheck ------------------------------ #
@message_bp.get('/healthCheck')
def index():
    response = Response("Message Endpoint")
    response.status_code = 200
    return response


# ------------------------------ /message/send_broadcast ------------------------------ #
@message_bp.post('/send_broadcast')
def send_broadcast():
    body = request.get_json()
    email = body.get("user_email")
    title = body.get("title")
    message_body = body.get("body")
    timestamp = body.get("timestamp")

    user_id = get_user_id_by_email(email)
    if not user_id:
        return jsonify({'message': 'User not found'}), 404

    if not check_role_authorization(Roles.GOVT.name, request.authorization.token):
        return jsonify({'message': 'Unauthorized Request'}), 403

    responseMessage, errorMessage = send_notification(title, message_body, "send_broadcast")

    if errorMessage:
        return jsonify({'message': errorMessage}), 400

    new_broadcast = BroadcastMessage(
        title=title,
        message=message_body,
        timestamp=datetime.fromisoformat(timestamp)
    )
    db.session.add(new_broadcast)
    db.session.commit()

    return jsonify({'message': responseMessage}), 200


# ------------------------------ /message/broadcast ------------------------------ #
@message_bp.get('/broadcasts')
def get_broadcasts():
    messages = BroadcastMessage.query.order_by(BroadcastMessage.timestamp.desc()).all()
    results = [{
        'message_id': message.message_id,
        'title': message.title,
        'message': message.message,
        'timestamp': message.timestamp.isoformat(), 
    } for message in messages]

    return jsonify(results), 200