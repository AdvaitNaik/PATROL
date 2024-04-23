# models to map python classes to database tables
from src.database.db import db
from sqlalchemy.orm import relationship

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    uuid = db.Column(db.String(100), nullable=False)
    uuid_hash = db.Column(db.String(100), nullable=False)
    role_name = db.Column(db.String(100), nullable=False)
    fcm_reg_token = db.Column(db.TEXT, nullable=True)

    # Relationships
    locations = relationship("LocationHistory", backref="user", lazy='dynamic')
    vaccination_records = relationship("VaccinationHistory", backref="user", lazy='dynamic')
    infection_records = relationship("InfectionHistory", backref="user", lazy='dynamic')
    survey_demands = relationship("SkuDemandSurvey", backref="user", lazy='dynamic')


class BroadcastMessage(db.Model):
    __tablename__ = 'broadcast_messages'

    message_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)


class LocationHistory(db.Model):
    __tablename__ = 'location_history'

    location_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)


class VaccinationHistory(db.Model):
    __tablename__ = 'vaccination_history'

    vaccination_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    vaccination_date = db.Column(db.Date)


class InfectionHistory(db.Model):
    __tablename__ = 'infection_history'

    history_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    infected = db.Column(db.Boolean, nullable=False)
    symptoms = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, nullable=False)


class SkuDemandSurvey(db.Model):
    __tablename__ = 'sku_demand_survey'

    demand_id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    sku_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, nullable=False)

