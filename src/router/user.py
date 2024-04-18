from flask import Blueprint, Response, request, jsonify
from src.firebase import authenticate_user as firebase_authenticate_user, create_user as firebase_create_user
from src.database.model import User
from src.database.db import db

user_bp = Blueprint('user', __name__)


# ------------------------------ /user/healthCheck ------------------------------ #
@user_bp.get('/healthCheck')
def index():  
    response = Response("User Endpoint")
    response.status_code = 200
    return response


# ------------------------------ /user/<int:user_id> ------------------------------ #
@user_bp.get('/<int:user_id>')
def user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    user_data = {
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone_number": user.phone_number,
        "email": user.email,
        "address": user.address,
        "city": user.city,
        "state": user.state,
        "country": user.country,
        "zip_code": user.zip_code,
        "latitude": user.latitude,
        "longitude": user.longitude,
        "role_name": user.role.role_name if user.role else None
    }
    return jsonify(user_data), 200


# ------------------------------ /user/login ------------------------------ #
@user_bp.post('/login')
def user_login():
    body = request.get_json()
    email = body.get("email")
    password = body.get("password")

    result = firebase_authenticate_user(email, password)
    if 'token' in result:
        return jsonify({"token": result['token']}), 200
    else:
        return jsonify({"error": result['error']}), 401
    

# ------------------------------ /user/create ------------------------------ #
@user_bp.post('/create')
def user_create():
    body = request.get_json()
    email = body.get("email")
    password = body.get("password")
    username = body.get("username")

    try:
        user_status, user_uid = firebase_create_user(email, password, username)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    new_user = User(
        username=username,
        first_name=body.get("first_name"),
        last_name=body.get("last_name"),
        email=email,
        phone_number=body.get("phone_number", ""),
        address=body.get("address", ""),
        city=body.get("city", ""),
        state=body.get("state", ""),
        country=body.get("country", ""),
        zip_code=body.get("zip_code", ""),
        latitude=body.get("latitude", 0.0),
        longitude=body.get("longitude", 0.0),
        role_id=body.get("role_id")
    )

    if user_status:
        db.session.add(new_user)
        db.session.commit()

    return jsonify({"message": "User created successfully", "user_name": new_user.username}), 201




# @user_bp.post('/create_user')
# def create_new_user():
#     body = request.get_json()
#     message = create_user(body.get("email"), body.get("password"), body.get("fullname"), body.get("claims"))
#     response = Response(message)
#     response.status_code = 200
#     response.headers.add("Access-Control-Allow-Origin", "*")
#     response.headers.add('Access-Control-Allow-Headers', "*")
#     response.headers.add('Access-Control-Allow-Methods', "*")
#     return response
