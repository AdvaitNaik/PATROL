from flask import Blueprint, Response, request, jsonify
from src.utils.firebase import send_notification, check_role_authorization, Roles

message_bp = Blueprint('message', __name__)


@message_bp.get('/')
def index():
    response = Response("Message Endpoint")
    response.status_code = 200
    return response


@message_bp.post('/send_notification')
def send_notifications():
    if not check_role_authorization(Roles.GOVT.name, request.authorization.token):
        return jsonify({'message': 'Unauthorized Request'}), 403

    body = request.get_json()
    responseMessage, errorMessage = send_notification(body.get("title"), body.get("body"), "exposure")

    if errorMessage:
        response = Response(errorMessage)
        response.status_code = 400
    else:
        response = Response(responseMessage)
        response.status_code = 200

    return response
