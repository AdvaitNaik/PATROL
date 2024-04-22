from flask import Blueprint, Response, request, jsonify
from src.database.model import SkuDemandSurvey, VaccinationHistory, InfectionHistory, User
from src.utils.firebase import check_role_authorization, Roles
from src.database.db import db
from sqlalchemy import func, distinct
from datetime import datetime, timedelta

research_bp = Blueprint('research', __name__)


# ------------------------------ Util Methods ------------------------------ #
def fetch_all_cities_demand(yesterday, today, last_week_start, last_month_start):
    products = ["sanitizer", "toilet paper", "mask", "disinfectant wipes"]

    def demand_for_period(start_date, end_date):
        results = db.session.query(
            SkuDemandSurvey.city,
            SkuDemandSurvey.sku_name,
            func.sum(SkuDemandSurvey.quantity).label('total_quantity')
        ).filter(
            SkuDemandSurvey.sku_name.in_(products),
            SkuDemandSurvey.timestamp >= start_date,
            SkuDemandSurvey.timestamp <= end_date
        ).group_by(SkuDemandSurvey.city, SkuDemandSurvey.sku_name).all()

        city_demand = {}
        for result in results:
            if result.city.title() not in city_demand:
                city_demand[result.city.title()] = {}
            city_demand[result.city.title()][result.sku_name.title()] = result.total_quantity
        return city_demand

    return {
        "Yesterday Demand": demand_for_period(yesterday, today),
        "Past Week Demand": demand_for_period(last_week_start, today),
        "Past Month Demand": demand_for_period(last_month_start, today)
    }


# ------------------------------ /research/healthCheck ------------------------------ #
@research_bp.get('/healthCheck')
def index():  
    response = Response("Research Endpoint")
    response.status_code = 200
    return response


# ------------------------------ /research/infection_history ------------------------------ #
@research_bp.get('/infection_history')
def infection_records():

    if not check_role_authorization(Roles.RES.name, request.authorization.token):
        return jsonify({'message': 'Unauthorized Request'}), 403

    results = [
        {
            "History Id": record.history_id,
            "User Id": record.user_id,
            "Infected": record.infected,
            "Symptoms": record.symptoms,
            "Timestamp": record.timestamp.isoformat() if record.timestamp else None
        }
        for record in InfectionHistory.query.all()
    ]

    return jsonify(results), 200

# ------------------------------ /research/vaccination_history ------------------------------ #
@research_bp.get('/vaccination_history')
def vaccination_records():

    if not check_role_authorization(Roles.RES.name, request.authorization.token):
        return jsonify({'message': 'Unauthorized Request'}), 403

    results = [
        {
            "Vaccination Id": record.vaccination_id,
            "User Id": record.user_id,
            "Vaccination Date": record.vaccination_date.isoformat() if record.vaccination_date else None
        }
        for record in VaccinationHistory.query.all()
    ]

    return jsonify(results), 200


# ------------------------------ /research/ecommerce_insights/<city> ------------------------------ #
@research_bp.get('/ecommerce_insights')
def get_demand():
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=2)
    last_week_start = today - timedelta(days=7)
    last_month_start = today - timedelta(days=30)
    
    demands = fetch_all_cities_demand(yesterday, today, last_week_start, last_month_start)

    # if not check_role_authorization(Roles.RES.name, request.authorization.token):
    #     return jsonify({'message': 'Unauthorized Request'}), 403

    return jsonify(demands), 200

