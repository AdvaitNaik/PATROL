from flask import Blueprint, Response, request

government_bp = Blueprint('government', __name__)

government_bp.get('/')
def index():  
    response = Response("Government Endpoint")
    response.status_code = 200
    return response