from flask import Blueprint, Response, request
from src.firebase import send_notification

message_bp = Blueprint('message', __name__)

@message_bp.get('/')
def index():  
    response = Response("Message Endpoint")
    response.status_code = 200
    return response

@message_bp.post('/send_notification')
def send_notifications():
    body = request.get_json()
    responseMessage, errorMessage = send_notification(body.get("title"), body.get("body"), body.get("topic"))

    if errorMessage:
        response = Response(errorMessage)
        response.status_code = 400
    else:
        response = Response(responseMessage)
        response.status_code = 200

    # response.headers.add("Access-Control-Allow-Origin", "*")
    # response.headers.add('Access-Control-Allow-Headers', "*")
    # response.headers.add('Access-Control-Allow-Methods', "*")
    return response