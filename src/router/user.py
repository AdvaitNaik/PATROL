from flask import Blueprint, Response, request, jsonify
from src.utils.firebase import check_email_authorization, create_user as firebase_create_user
from src.database.model import User
from src.database.db import db
import uuid
import hashlib

user_bp = Blueprint('user', __name__)


# ------------------------------ Util Methods ------------------------------ #
def create_uuid_hash(uuid: str):
    sha1 = hashlib.sha1()
    sha1.update(uuid.encode('utf-8'))
    hashed_uuid = sha1.hexdigest()
    return hashed_uuid


# ------------------------------ /user/healthCheck ------------------------------ #
@user_bp.get('/healthCheck')
def index():  
    response = Response("User Endpoint")
    response.status_code = 200
    return response


# ------------------------------ /user/<int:user_id> ------------------------------ #
@user_bp.get('/info')
def user():
    body = request.get_json()
    user_email = body.get("user_email")

    if not check_email_authorization(user_email, request.authorization.token):
        return jsonify({'message': 'Unauthorized Request'}), 403

    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    user_data = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "uuid": user.uuid,
        "uuid_hash": user.uuid_hash,
        "role_name": user.role_name
    }

    return jsonify(user_data), 200


# ------------------------------ /user/create ------------------------------ #
@user_bp.post('/create')
def user_create():
    body = request.get_json()
    email = body.get("email")
    password = body.get("password")
    role_name = body.get("role_name")
    first_name = body.get("first_name"),
    last_name = body.get("last_name")
    print(role_name)

    try:
        user_create_status = firebase_create_user(email=email, password=password, fullname=f"{first_name} {last_name}", role_name=role_name)
    except Exception as e:
        return jsonify({"Error": str(e)}), 400

    user_uuid = uuid.uuid4()
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        uuid=user_uuid,
        uuid_hash=create_uuid_hash(str(user_uuid)),
        role_name=role_name
    )

    if user_create_status:
        db.session.add(new_user)
        db.session.commit()

    return jsonify({"message": "User created successfully", "user_uuid": body}), 201



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
