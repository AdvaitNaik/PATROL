from flask import Blueprint, Response, request, jsonify
from src.utils.firebase import check_email_authorization, create_user as firebase_create_user
from src.database.model import User, SkuDemandSurvey, LocationHistory, VaccinationHistory, InfectionHistory
from src.database.db import db
from datetime import datetime
import uuid
import hashlib

user_bp = Blueprint('user', __name__)


# ------------------------------ Util Methods ------------------------------ #
def create_uuid_hash(uuid: str):
    sha1 = hashlib.sha1()
    sha1.update(uuid.encode('utf-8'))
    hashed_uuid = sha1.hexdigest()
    return hashed_uuid

def get_user_id_by_email(email):
    user = User.query.filter_by(email=email).first()
    return user.user_id if user else None


# ------------------------------ /user/healthCheck ------------------------------ #
@user_bp.get('/healthCheck')
def index():  
    response = Response("User Endpoint")
    response.status_code = 200
    return response


# ------------------------------ /user/<int:user_id> ------------------------------ #
@user_bp.post('/info')
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


# ------------------------------ /user/request_items ------------------------------ #
@user_bp.post('/request_items')
def populate_sku_demand():
    body = request.get_json()
    email = body.get("user_email")
    items = body.get("items")
    city = body.get("city")
    survery_id = body.get("survery_id")

    user_id = get_user_id_by_email(email)
    if not user_id:
        return jsonify({'message': 'User not found'}), 404

    for index, item in enumerate(items, start=1):
        demand = SkuDemandSurvey(
            user_id=user_id,
            survey_id=survery_id,  
            city=city.lower(),
            sku_name=item.lower(),
            ranking=index,
            quantity=1 
        )
        db.session.add(demand)

    db.session.commit()
    return jsonify({"message": "SKU demand added successfully"}), 201


# ------------------------------ /user/request_items ------------------------------ #
@user_bp.post('/populate_location')
def populate_location_history():
    body = request.get_json()
    email = body.get("user_email")
    latitude = body.get("latitude")
    longitude = body.get("longitude")
    timestamp = body.get("timestamp")

    user_id = get_user_id_by_email(email)
    if not user_id:
        return jsonify({'message': 'User not found'}), 404

    location = LocationHistory(
        user_id=user_id,
        latitude=latitude,
        longitude=longitude,
        timestamp = datetime.fromisoformat(timestamp)
    )
    db.session.add(location)
    db.session.commit()

    return jsonify({"message": "Location history added successfully"}), 201


# ------------------------------ /user/update_vaccination ------------------------------ #
@user_bp.post('/update_vaccination')
def update_vaccination():
    body = request.get_json()
    email = body.get("user_email")
    vaccination_date = body.get("vaccination_date")

    user_id = get_user_id_by_email(email)
    if not user_id:
        return jsonify({'message': 'User not found'}), 404

    vaccination = VaccinationHistory(
        user_id=user_id,
        vaccination_date=datetime.strptime(vaccination_date, '%Y-%m-%d').date()
    )
    db.session.add(vaccination)
    db.session.commit()

    return jsonify({"message": "Vaccination history updated successfully"}), 201


# ------------------------------ /user/update_infection ------------------------------ #
@user_bp.post('/update_infection')
def update_infection():
    body = request.get_json()
    email = body.get("user_email")
    infected = body.get("infected")
    symptoms = body.get("symptoms")
    timestamp = body.get("timestamp")

    user_id = get_user_id_by_email(email)
    if not user_id:
        return jsonify({'message': 'User not found'}), 404

    new_infection = InfectionHistory(
        user_id=user_id,
        infected=infected,
        symptoms=symptoms.lower(),
        timestamp=datetime.fromisoformat(timestamp)
    )
    db.session.add(new_infection)
    db.session.commit()

    return jsonify({"message": "Infection history updated successfully"}), 201



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
