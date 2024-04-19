from flask import Blueprint, Response, request

ecommerce_bp = Blueprint('ecommerce', __name__)

ecommerce_bp.get('/')
def index():  
    response = Response("Ecommerce Endpoint")
    response.status_code = 200
    return response