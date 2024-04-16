from flask import Blueprint, Response, request
from src.firebase import create_user

user_bp = Blueprint('user', __name__)

@user_bp.get('/')
def index():  
    response = Response("User Endpoint")
    response.status_code = 200
    return response

@user_bp.post('/create_user')
def create_new_user():
    body = request.get_json()
    message = create_user(body.get("email"), body.get("password"), body.get("fullname"), body.get("claims"))
    response = Response(message)
    response.status_code = 200
    # response.headers.add("Access-Control-Allow-Origin", "*")
    # response.headers.add('Access-Control-Allow-Headers', "*")
    # response.headers.add('Access-Control-Allow-Methods', "*")
    return response
