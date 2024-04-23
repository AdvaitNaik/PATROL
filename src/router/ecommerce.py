from urllib.parse import unquote
from flask import Blueprint, Response, request, jsonify
from sqlalchemy import func
from datetime import datetime, timedelta
from src.database.model import SkuDemandSurvey
from src.utils.firebase import check_role_authorization, Roles
from src.database.db import db

ecommerce_bp = Blueprint('ecommerce', __name__)

# ------------------------------ Util Methods ------------------------------ #
def fetch_demand(city, start_date, end_date):
    products = ["sanitizer", "tissue paper", "mask", "bread"]

    results = db.session.query(
        SkuDemandSurvey.sku_name,
        func.sum(SkuDemandSurvey.quantity).label('total_quantity')
    ).filter(
        SkuDemandSurvey.city == city.lower(),
        SkuDemandSurvey.sku_name.in_(products),
        SkuDemandSurvey.timestamp >= start_date,
        SkuDemandSurvey.timestamp <= end_date
    ).group_by(SkuDemandSurvey.sku_name).all()

    return {result.sku_name.title(): result.total_quantity for result in results}

# ------------------------------ /ecommerce/healthCheck ------------------------------ #
@ecommerce_bp.get('/healthCheck')
def index():  
    response = Response("Ecommerce Endpoint")
    response.status_code = 200
    return response

# ------------------------------ /ecommerce/demand/<city> ------------------------------ #
@ecommerce_bp.get('/demand/<city>')
def get_city_demand(city):
    city = unquote(city)
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)
    last_week_start = today - timedelta(days=7)
    last_month_start = today - timedelta(days=30)
    yesterday_demand = fetch_demand(city, yesterday, today)
    last_week_demand = fetch_demand(city, last_week_start, today)
    last_month_demand = fetch_demand(city, last_month_start, today)

    if not (check_role_authorization(Roles.ECOMM.name, request.authorization.token) or
            check_role_authorization(Roles.GOVT.name, request.authorization.token)):
        return jsonify({'message': 'Unauthorized Request'}), 403

    return jsonify({
        "city": city,
        "Yesterday Demand": yesterday_demand,
        "Past Week Demand": last_week_demand,
        "Past Month Demand": last_month_demand
    }), 200
