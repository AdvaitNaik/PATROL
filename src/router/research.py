from flask import Blueprint, Response, request, jsonify
from src.database.model import SkuDemandSurvey, VaccinationHistory, InfectionHistory, User
from src.utils.firebase import check_role_authorization, Roles
from src.database.db import db
from sqlalchemy import func, distinct
from datetime import datetime, timedelta

research_bp = Blueprint('research', __name__)


# ------------------------------ Util Methods ------------------------------ #
def fetch_vaccination_record():
    result = db.session.query(func.count(distinct(VaccinationHistory.user_id))).scalar()
    return result

def fetch_infection_record():
    result = db.session.query(func.count(distinct(InfectionHistory.user_id))).filter(InfectionHistory.infected == True).scalar()
    return result

def fetch_demand(city, start_date, end_date):
    products = ["sanitizer", "toilet paper", "mask", "disinfectant wipes"]

    results = db.session.query(
        SkuDemandSurvey.sku_name,
        func.sum(SkuDemandSurvey.quantity).label('total_quantity')
    ).filter(
        SkuDemandSurvey.city == city.lower(),
        SkuDemandSurvey.sku_name.in_(products),
        SkuDemandSurvey.timestamp >= start_date,
        SkuDemandSurvey.timestamp <= end_date
    ).group_by(SkuDemandSurvey.sku_name).all()

    return {result.sku_name: result.total_quantity for result in results}


# ------------------------------ /research/healthCheck ------------------------------ #
@research_bp.get('/healthCheck')
def index():  
    response = Response("Research Endpoint")
    response.status_code = 200
    return response


# ------------------------------ /research/infection_history ------------------------------ #
@research_bp.get('/infection_history')
def infection_records():

    # if not check_role_authorization(Roles.RES.name, request.authorization.token):
    #     return jsonify({'message': 'Unauthorized Request'}), 403

    results = [
        {
            "History ID": record.history_id,
            "User UUID": record.uuid,
            "Infected": record.infected,
            "Symptoms": record.symptoms,
            "Timestamp": record.timestamp.isoformat() if record.timestamp else None 
        }
        for record in db.session.query(
            InfectionHistory.history_id,
            User.uuid,
            InfectionHistory.infected,
            InfectionHistory.symptoms,
            InfectionHistory.timestamp
        ).join(User, InfectionHistory.user_id == User.user_id).filter(InfectionHistory.infected == True).all()
    ]

    return jsonify(results), 200

# ------------------------------ /research/vaccination_history ------------------------------ #
@research_bp.get('/vaccination_history')
def vaccination_records():
    vaccinated_count = fetch_vaccination_record()

    if not check_role_authorization(Roles.RES.name, request.authorization.token):
        return jsonify({'message': 'Unauthorized Request'}), 403

    return jsonify({
        "Total Vaccinated": vaccinated_count
    }), 200


# ------------------------------ /research/ecommerce_insights/<city> ------------------------------ #
@research_bp.get('/ecommerce_insights/<city>')
def get_city_demand(city):
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=2)
    last_week_start = today - timedelta(days=7)
    last_month_start = today - timedelta(days=30)
    yesterday_demand = fetch_demand(city, yesterday, today)
    last_week_demand = fetch_demand(city, last_week_start, today)
    last_month_demand = fetch_demand(city, last_month_start, today)

    if not check_role_authorization(Roles.RES.name, request.authorization.token):
        return jsonify({'message': 'Unauthorized Request'}), 403


    return jsonify({
        "city": city,
        "Yesterday Demand": yesterday_demand,
        "Past Week Demand": last_week_demand,
        "Past Month Demand": last_month_demand
    }), 200

