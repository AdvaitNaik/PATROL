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

    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(message_bp, url_prefix='/message')
    app.register_blueprint(crowd_bp, url_prefix='/crowd')

    @app.route('/hello')
    def index():
        return "This is from flask backend", 200

    return app



# @app.get('/hello')
# def index(): 
#     response = Response("This is from flask backend")
#     response.status_code = 200
#     response.headers.add("Access-Control-Allow-Origin", "*")
#     response.headers.add('Access-Control-Allow-Headers', "*")
#     response.headers.add('Access-Control-Allow-Methods', "*")
#     return response


# @app.post('/create_user')
# def create_new_user():
#     body = request.get_json()
#     message = create_user(body.get("email"), body.get("password"), body.get("fullname"), body.get("claims"))
#     response = Response(message)
#     response.status_code = 200
#     response.headers.add("Access-Control-Allow-Origin", "*")
#     response.headers.add('Access-Control-Allow-Headers', "*")
#     response.headers.add('Access-Control-Allow-Methods', "*")
#     return response


# @app.post('/send_notification')
# def send_notifications():
#     body = request.get_json()
#     responseMessage, errorMessage = send_notification(body.get("title"), body.get("body"), body.get("topic"))

#     if errorMessage:
#         response = Response(errorMessage)
#         response.status_code = 400
#     else:
#         response = Response(responseMessage)
#         response.status_code = 200

#     response.headers.add("Access-Control-Allow-Origin", "*")
#     response.headers.add('Access-Control-Allow-Headers', "*")
#     response.headers.add('Access-Control-Allow-Methods', "*")
#     return response


# if __name__ == '__main__':
#     app.run(host="localhost", port=5000)
