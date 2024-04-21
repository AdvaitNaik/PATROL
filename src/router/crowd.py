from flask import Blueprint, Response, jsonify, abort, request
from src.database.model import LocationHistory, InfectionHistory
from geoalchemy2 import Geography
from geoalchemy2.functions import ST_DWithin, ST_SetSRID, ST_GeomFromText
from datetime import datetime, timedelta
from math import radians, cos, sin, asin, sqrt

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


# ------------------------------ /crowd/healthCheck ------------------------------ #
@crowd_bp.get('/healthCheck')
def index():  
    response = Response("Crowd Monitoring Endpoint")
    response.status_code = 200
    return response


@crowd_bp.post('/map/monitor')
def crowd_monitor_map():

    data = request.get_json()
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])

    radius_km = 1.609  # 1 mile in kilometers

    nearby_locations = []
    all_locations = LocationHistory.query.all()
    for location in all_locations:
        if haversine(longitude, latitude, location.longitude, location.latitude) <= radius_km:
            nearby_locations.append(location)

    unique_user_ids = {location.user_id for location in nearby_locations}
    total_number_of_people = len(unique_user_ids)

    total_infected = InfectionHistory.query.filter(
        InfectionHistory.user_id.in_(unique_user_ids),
        InfectionHistory.infected == True
    ).count()

    locations = [{
        "latitude": location.latitude,
        "longitude": location.longitude,
        "isInfected": bool(InfectionHistory.query.filter(
            InfectionHistory.user_id == location.user_id, 
            InfectionHistory.infected == True).first())
    } for location in nearby_locations]

    return jsonify({
        "totalNumberOfPeople": total_number_of_people,
        "totalInfected": total_infected,
        "locations": locations
    }), 200


@crowd_bp.post('/trend/monitor')
def crowd_monitor_trend():
    data = request.get_json()
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    days = int(data.get('days', 0))

    radius_km = 1.609  # 1 mile in kilometers

    if days < 0:
        start_time = datetime.utcnow() + timedelta(days=days)
        end_time = datetime.utcnow()
    else:
        start_time = datetime.utcnow()
        end_time = start_time 

    nearby_locations = []
    all_locations = LocationHistory.query.filter(
        LocationHistory.timestamp >= start_time,
        LocationHistory.timestamp <= end_time
    ).all()

    for location in all_locations:
        if haversine(longitude, latitude, location.longitude, location.latitude) <= radius_km:
            nearby_locations.append(location)

    unique_user_ids = {location.user_id for location in nearby_locations}
    total_number_of_people = len(unique_user_ids)

    total_infected = InfectionHistory.query.filter(
        InfectionHistory.user_id.in_(unique_user_ids),
        InfectionHistory.infected == True,
        InfectionHistory.timestamp >= start_time,
        InfectionHistory.timestamp <= end_time
    ).count()

    locations = [{
        "latitude": location.latitude,
        "longitude": location.longitude,
        "isInfected": bool(InfectionHistory.query.filter(
            InfectionHistory.user_id == location.user_id,
            InfectionHistory.infected == True,
            InfectionHistory.timestamp >= start_time,
            InfectionHistory.timestamp <= end_time
        ).first())
    } for location in nearby_locations]

    return jsonify({
        "totalNumberOfPeople": total_number_of_people,
        "totalInfected": total_infected,
        "locations": locations
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