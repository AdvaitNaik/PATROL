from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

from src.utils.logger import Logger
logger = Logger("database").logger

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)

def get_database():
    return db

def test_connection():
    with db.app.app_context():  
        try:
            db.session.execute(text('SELECT 1'))
            logger.info("Database connection successful.")
        except Exception as e:
            logger.error(f"Error connecting to the database: {e}")

if __name__ == "__main__":
    test_connection()
