import datetime
import json
from enum import Enum

import firebase_admin
from firebase_admin import credentials, messaging, auth
from src.settings import config

from src.utils.logger import Logger

logger = Logger("firebase").logger

FIREBASE_CREDENTIALS = json.loads(config.FIREBASE_CONFIG)
cred = credentials.Certificate(FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred)

Roles = Enum('Roles', ['GEN', 'GOVT', 'RES', 'ECOMM'])

# ------------------------------ authorization ------------------------------ #
def check_email_authorization(email, id_token) -> bool:
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token.get('email') == email
    except Exception as e:
        logger.error(e)
        return False


def check_role_authorization(role, id_token) -> bool:
    try:
        decode_token = auth.verify_id_token(id_token)
        logger.info(role, decode_token)
        return decode_token.get(role) is not None and decode_token.get(role)
    except Exception as e:
        logger.error(e)
        return False


# ------------------------------ user ------------------------------ #
def create_user(email, password, fullname, role_name):
    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=fullname
        )
    except Exception as e:
        logger.exception(f"Failed to create user - {e}")
        return Exception("Failed to create user")

    roles_json = {role_name: True}
    auth.set_custom_user_claims(user.uid, roles_json)
    logger.info('Successfully created new user: {0}'.format(user.uid))
    return True


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


# ------------------------------ notification ------------------------------ #
def send_notification_to_device(title: str, body: str, reg_ids: list):
    logger.info("send_notification_to_device")
    message = messaging.MulticastMessage(
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
        tokens=reg_ids
    )

    try:
        response = messaging.send_multicast(message)
        logger.info(response)
    except Exception as e:
        error_message = "Failed to send notification: " + str(e)
        logger.info(error_message)
