from flask import Blueprint, Response, request, jsonify
from sqlalchemy import func, distinct
from src.database.model import User, VaccinationHistory, InfectionHistory
from src.utils.firebase import check_role_authorization, Roles
from src.database.db import db

government_bp = Blueprint('government', __name__)


# ------------------------------ Util Methods ------------------------------ #
def fetch_vaccination_record():
    result = db.session.query(func.count(distinct(VaccinationHistory.user_id))).scalar()
    return result

def fetch_infection_record():
    result = db.session.query(func.count(distinct(InfectionHistory.user_id))).filter(InfectionHistory.infected == True).scalar()
    return result

def fetch_total_users():
    result = db.session.query(func.count(distinct(User.user_id))).scalar()
    return result


# ------------------------------ /government/healthCheck ------------------------------ #
@government_bp.get('/healthCheck')
def index():  
    response = Response("Government Endpoint")
    response.status_code = 200
    return response


# ------------------------------ /government/health_records ------------------------------ #
@government_bp.get('/health_records')
def health_records():

    if not check_role_authorization(Roles.GOVT.name, request.authorization.token):
        return jsonify({'message': 'Unauthorized Request'}), 403

    vaccinated_count = fetch_vaccination_record()
    infected_count = fetch_infection_record()
    total_users = fetch_total_users()

    return jsonify({
        "Total Users": total_users,
        "Total Vaccinated": vaccinated_count,
        "Total Infected": infected_count
    }), 200