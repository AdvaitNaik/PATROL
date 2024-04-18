import datetime
import json

import firebase_admin
from firebase_admin import credentials, messaging, auth
from src.settings import config  

from src.utils.logger import Logger
logger = Logger("firebase").logger

# from dotenv import load_dotenv
# load_dotenv()

# FIREBASE_CREDENTIALS = json.loads(os.getenv('FIREBASE_CONFIG'))
FIREBASE_CREDENTIALS = json.loads(config.FIREBASE_CONFIG)
cred = credentials.Certificate(FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred)


# def create_user(email, password, name, claims):
#     try:
#         user = auth.create_user(
#             email=email,
#             password=password,
#             display_name=name
#         )
#     except Exception as e:
#         print(e)
#         return "Failed to create user"

#     claims_json = {}
#     for claim in claims:
#         claims_json[claim] = True
#     auth.set_custom_user_claims(user.uid, claims_json)
#     print('Successfully created new user: {0}'.format(user.uid))
#     return 'Successfully created new user: {0}'.format(user.uid)

# ------------------------------ user ------------------------------ #
def create_user(email, password, username):
    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=username
        )
    except Exception as e:
        logger.exception(f"Failed to create user - {e}")
        return Exception("Failed to create user")

    logger.info('Successfully created new user: {0}'.format(user.uid))
    return (True, user.uid)

def authenticate_user(email, password):
    """Authenticate user using Firebase Authentication.
    """
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        token = user['idToken']
        return {'token': token}
    except Exception as e:
        return {'error': str(e)}


# ------------------------------ notification ------------------------------ #
def send_notification(title: str, body: str, topic: str):
    if not title or not body or not topic:
        return None, "ERROR : Title, body and topic must not be empty."

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        android=messaging.AndroidConfig(
            ttl=datetime.timedelta(seconds=3600),
            priority='normal',
            notification=messaging.AndroidNotification(
                icon='stock_ticker_update',
                color='#f45342'
            ),
        ),
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(badge=42),
            ),
        ),
        topic=topic,
    )

    try:
        response = messaging.send(message)
        logger.info("Notification sent successfully:", response)
        return 'Notification sent!', None
    except Exception as e:
        error_message = "Failed to send notification: " + str(e)
        logger.error(error_message)
        return None, "Failed to send notification"


# create_user("trino.nandi@gmail.com", "Trinanjan@00", "Trinanjan")
# send_notification("Trinanjan", "Hey it's me broadcasting to all devices registered", "broadcast")
# send_notification("Trinanjan", "Exposure notification!!!", "exposure")