from flask import Blueprint, Response, request

research_bp = Blueprint('research', __name__)

research_bp.get('/')
def index():  
    response = Response("Research Endpoint")
    response.status_code = 200
    return response