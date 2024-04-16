from flask import Blueprint, Response, jsonify, abort
from src.database.model import LocationHistory, InfectionHistory
# from src.database.db import db

crowd_bp = Blueprint('crowd', __name__)

@crowd_bp.get('/')
def index():  
    response = Response("Crowd Monitoring Endpoint")
    response.status_code = 200
    return response

# ------------------------------get_location_history------------------------------
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


# ------------------------------get_infection_history------------------------------
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