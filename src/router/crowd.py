from flask import Blueprint, Response, jsonify, abort, request
from src.database.db import db
from src.database.model import LocationHistory, InfectionHistory
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
from src.utils.ml import regression_model
from math import radians, cos, sin, asin, sqrt
from sqlalchemy import func, select
import random

crowd_bp = Blueprint('crowd', __name__)


# ------------------------------ Util Methods ------------------------------ #
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371  
    return c * r


def get_latest_location_records():
    latest_timestamp_subquery = (
        db.session.query(LocationHistory.user_id, func.max(LocationHistory.timestamp).label("max_timestamp"))
            .group_by(LocationHistory.user_id)
            .subquery())
    
    latest_records = (
        db.session.query(LocationHistory)
            .join(
            latest_timestamp_subquery,
            (LocationHistory.user_id == latest_timestamp_subquery.c.user_id)
            & (LocationHistory.timestamp == latest_timestamp_subquery.c.max_timestamp)
        )
            .all()
    )
    return latest_records

# ------------------------------ /crowd/healthCheck ------------------------------ #
@crowd_bp.get('/healthCheck')
def index():  
    response = Response("Crowd Monitoring Endpoint")
    response.status_code = 200
    return response

# ------------------------------ /crowd/map/monitor ------------------------------ #
@crowd_bp.post('/map/monitor')
def crowd_monitor_map():
    data = request.get_json()
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])

    radius_km = 16.09  # 10 mile in kilometers

    all_locations = get_latest_location_records()
    # all_locations = LocationHistory.query.all()
    nearby_locations = [loc for loc in all_locations if haversine(longitude, latitude, loc.longitude, loc.latitude) <= radius_km]

    unique_user_ids = {loc.user_id for loc in nearby_locations}

    infected_user_ids = InfectionHistory.query.filter(
        InfectionHistory.user_id.in_(unique_user_ids),
        InfectionHistory.infected == True
    ).with_entities(InfectionHistory.user_id).distinct().all()

    total_number_of_people = len(unique_user_ids)
    total_infected = len(infected_user_ids)

    locations = [{
        "latitude": loc.latitude,
        "longitude": loc.longitude,
        "isInfected": bool(InfectionHistory.query.filter(
            InfectionHistory.user_id == loc.user_id,
            InfectionHistory.infected == True).first())
    } for loc in nearby_locations]
    # print(locations)
    return jsonify({
        "totalNumberOfPeople": total_number_of_people,
        "totalInfected": total_infected,
        "locations": locations
    }), 200


# ------------------------------ /crowd/trend/monitor ------------------------------ #
@crowd_bp.post('/trend/monitor')
def crowd_monitor_trend():
    data = request.get_json()
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    days = int(data.get('days', 0))

    radius_km = 16.09  # 10 mile in kilometers

    today = datetime.utcnow().date()
    if days < 0:
        start_time = today + timedelta(days=days-1)
        end_time = today - timedelta(days=1)
    elif days > 0:
        predicted_visits, predicted_infections = regression_model(latitude, longitude, days)
        return jsonify({
            "totalNumberOfPeople": int(predicted_visits),
            "totalInfected": int(predicted_infections)
        }), 200
    else:
        start_time = today - timedelta(days=2)
        end_time = today - timedelta(days=1)

    all_locations = LocationHistory.query.filter(
        LocationHistory.timestamp >= start_time,
        LocationHistory.timestamp <= end_time
    ).all()
    nearby_locations = [loc for loc in all_locations if haversine(longitude, latitude, loc.longitude, loc.latitude) <= radius_km]

    unique_user_ids = {loc.user_id for loc in nearby_locations}

    infected_user_ids = InfectionHistory.query.filter(
        InfectionHistory.user_id.in_(unique_user_ids),
        InfectionHistory.infected == True,
        InfectionHistory.timestamp >= start_time,
        InfectionHistory.timestamp <= end_time
    ).with_entities(InfectionHistory.user_id).distinct().all()

    total_number_of_people = len(unique_user_ids)
    total_infected = len(infected_user_ids)  

    return jsonify({
        "totalNumberOfPeople": total_number_of_people,
        "totalInfected": total_infected
    }), 200


# ------------------------------ HIDDEN ENDPOINT ------------------------------ #
# ------------------------------ /crowd/location_history/<int:user_id> ------------------------------ #
@crowd_bp.get('/location_history/<int:user_id>')
def get_location_history(user_id):
    locations = LocationHistory.query.filter_by(user_id=user_id).all()

    if not locations:
        abort(404, description="No location history found for user_id: {}".format(user_id))

    location_list = [
        {
            "location_id": location.location_id,
            "user_id": location.user_id,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "reverse_geo_code_address": location.reverse_geo_code_address
        } for location in locations
    ]

    return jsonify(location_list), 200


# ------------------------------ /crowd/infection_history ------------------------------ #
@crowd_bp.get('/infection_history')
def get_infection_history():
    infections = InfectionHistory.query.all()
    infection_list = [
        {
            "history_id": infection.history_id,
            "user_id": infection.user_id,
            "infected": infection.infected,
            "symptoms": infection.symptoms,
            "timestamp": infection.timestamp.isoformat() if infection.timestamp else None
        } for infection in infections
    ]
    return jsonify(infection_list), 200