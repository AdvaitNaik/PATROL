# models to map python classes to database tables

from src.database.db import db
from sqlalchemy.orm import relationship

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(10))
    country_code = db.Column(db.String(5))
    email = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    zip_code = db.Column(db.String(10))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    messages = relationship("BroadcastMessage", backref="user", lazy='dynamic')
    locations = relationship("LocationHistory", backref="user", lazy='dynamic')
    infection_records = relationship("InfectionHistory", backref="user", lazy='dynamic')


class UserRole(db.Model):
    __tablename__ = 'user_roles'

    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), nullable=False)


class BroadcastMessage(db.Model):
    __tablename__ = 'broadcast_messages'

    message_id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)


class LocationHistory(db.Model):
    __tablename__ = 'location_history'

    location_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    reverse_geo_code_address = db.Column(db.String(100))
    

class InfectionHistory(db.Model):
    __tablename__ = 'infection_history'

    history_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    infected = db.Column(db.Boolean, nullable=False)
    symptoms = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, nullable=False)
