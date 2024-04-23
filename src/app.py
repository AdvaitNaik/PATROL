from flask import Flask, Response, Blueprint
from flask_cors import CORS
from src.database.db import init_db

from src.utils.logger import Logger
logger = Logger("app").logger


def create_patrol_app():
    app = Flask(__name__)
    CORS(app)

    from src.settings import config
    app.config['SQLALCHEMY_DATABASE_URI'] = config.POSTGRES_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS

    init_db(app)

    from src.router.user import user_bp
    from src.router.notification import message_bp
    from src.router.crowd import crowd_bp
    from src.router.government import government_bp
    from src.router.ecommerce import ecommerce_bp
    from src.router.research import research_bp

    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(message_bp, url_prefix='/message')
    app.register_blueprint(crowd_bp, url_prefix='/crowd')
    app.register_blueprint(government_bp, url_prefix='/government')
    app.register_blueprint(ecommerce_bp, url_prefix='/ecommerce')
    app.register_blueprint(research_bp, url_prefix='/research')

    @app.route('/healthCheck')
    def index():
        return "This is from flask backend", 200

    return app
