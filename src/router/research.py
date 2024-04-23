from flask import Blueprint, Response, request, jsonify
from src.database.model import SkuDemandSurvey, VaccinationHistory, InfectionHistory, User, LocationHistory, \
    BroadcastMessage
from src.utils.firebase import check_role_authorization, Roles
from src.database.db import db
from sqlalchemy import func, distinct
from datetime import datetime, timedelta

research_bp = Blueprint('research', __name__)


# ------------------------------ Util Methods ------------------------------ #
def fetch_all_cities_demand(yesterday, today, last_week_start, last_month_start):
    products = ["sanitizer", "tissue paper", "mask", "bread"]

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


# ------------------------------ /research/location_history ------------------------------ #
@research_bp.get('/location_history')
def location_records():
    if not check_role_authorization(Roles.RES.name, request.authorization.token):
        return jsonify({'message': 'Unauthorized Request'}), 403

    location_history_rows = LocationHistory.query.all()
    location_history_dicts = []
    for row in location_history_rows:
        location_history_dict = {
            'location_id': row.location_id,
            'user_id': row.user_id,
            'latitude': row.latitude,
            'longitude': row.longitude,
            'timestamp': row.timestamp.strftime("%Y-%m-%d %H:%M:%S")  # Convert datetime to string
        }
        location_history_dicts.append(location_history_dict)

    return jsonify(location_history_dicts),200

# ------------------------------ /research/infection_history ------------------------------ #
@research_bp.get('/infection_history')
def infection_records():

    if not check_role_authorization(Roles.RES.name, request.authorization.token):
        return jsonify({'message': 'Unauthorized Request'}), 403

    infection_history_rows = InfectionHistory.query.all()
    infection_history_dicts = []
    for row in infection_history_rows:
        infection_history_dict = {
            'history_id': row.history_id,
            'user_id': row.user_id,
            'infected': row.infected,
            'symptoms': row.symptoms,
            'timestamp': row.timestamp.strftime("%Y-%m-%d %H:%M:%S")  # Convert datetime to string
        }
        infection_history_dicts.append(infection_history_dict)

    return jsonify(infection_history_dicts),200

# ------------------------------ /research/vaccination_history ------------------------------ #
@research_bp.get('/vaccination_history')
def vaccination_records():
    if not check_role_authorization(Roles.RES.name, request.authorization.token):
        return jsonify({'message': 'Unauthorized Request'}), 403

    vaccination_history_rows = VaccinationHistory.query.all()
    vaccination_history_dicts = []
    for row in vaccination_history_rows:
        vaccination_history_dict = {
            'vaccination_id': row.vaccination_id,
            'user_id': row.user_id,
            'vaccination_date': row.vaccination_date.strftime("%Y-%m-%d %H:%M:%S")  # Convert datetime to string
        }
        vaccination_history_dicts.append(vaccination_history_dict)

    return jsonify(vaccination_history_dicts),200

# ------------------------------ /research/broadcast_history ------------------------------ #
@research_bp.get('/broadcast_history')
def broadcast_records():
    if not check_role_authorization(Roles.RES.name, request.authorization.token):
        return jsonify({'message': 'Unauthorized Request'}), 403

    broadcast_history_rows = BroadcastMessage.query.all()
    broadcast_history_dicts = []
    for row in broadcast_history_rows:
        broadcast_history_dict = {
            'message_id': row.message_id,
            'title': row.title,
            'message': row.message,
            'timestamp': row.timestamp.strftime("%Y-%m-%d %H:%M:%S")  # Convert datetime to string
        }
        broadcast_history_dicts.append(broadcast_history_dict)

    return jsonify(broadcast_history_dicts),200

# ------------------------------ /research/ecommerce_history ------------------------------ #
@research_bp.get('/ecommerce_history')
def ecommerce_records():
    if not check_role_authorization(Roles.RES.name, request.authorization.token):
        return jsonify({'message': 'Unauthorized Request'}), 403

    ecommerce_history_rows = SkuDemandSurvey.query.all()
    ecommerce_history_dicts = []
    for row in ecommerce_history_rows:
        ecommerce_history_dict = {
            'demand_id': row.demand_id,
            'survey_id': row.survey_id,
            'user_id': row.user_id,
            'city': row.city.title(),
            'sku_name' : row.sku_name.title(),
            'ranking':row.ranking,
            'quantity':row.quantity,
            'timestamp': row.timestamp.strftime("%Y-%m-%d %H:%M:%S")  # Convert datetime to string
        }
        ecommerce_history_dicts.append(ecommerce_history_dict)

    return jsonify(ecommerce_history_dicts),200

# ------------------------------ /research/ecommerce_insights ------------------------------ #
@research_bp.get('/ecommerce_insights')
def get_demand():
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=2)
    last_week_start = today - timedelta(days=7)
    last_month_start = today - timedelta(days=30)

    if not check_role_authorization(Roles.RES.name, request.authorization.token):
        return jsonify({'message': 'Unauthorized Request'}), 403
    
    demands = fetch_all_cities_demand(yesterday, today, last_week_start, last_month_start)

    return jsonify(demands), 200

