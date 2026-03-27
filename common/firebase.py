
import logging,os,firebase_admin,threading
from django.conf import settings
from firebase_admin import messaging,credentials
from JWTAuth.models import (FcmJson)
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)
fcm_executor = ThreadPoolExecutor(max_workers=20)

def init_firebase():
    """ 
      initialize firebase only once
      safe for Django auto reload 
      
    """
    firebase_obj = FcmJson.objects.filter(is_active=True).first()
    service_account_json = firebase_obj.json if firebase_obj else None
    # prevent multiple initialization
    if firebase_admin._apps:
        return
    # initialize firebase
    if not service_account_json:
        logger.warning("Firebase Service Account JSON not found")
        raise Exception("Firebase Service Account JSON not found")
    cred = credentials.Certificate(service_account_json)
    firebase_admin.initialize_app(cred)

def send_fcm_notification(payload:dict):
    """
      Send FCM Notification
      
    """
    logger.info(f"FCM Payload :: {payload}")
    token = payload.get("token")
    title = payload.get("title")
    body = payload.get("body")
    data = payload.get("data", {})
    logger.info(f"FCM Token :: {token}, Title :: {title}, Body :: {body}, Data :: {data}")
    if not token:
        logger.warning("FCM Token not found")
        return False
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body),
                android=messaging.AndroidConfig(
                    notification=messaging.AndroidNotification(
                        title=title,
                        body=body,
                        icon="ic_notification",
                        channel_id="buzzer_channel", 
                        color="#0A6ED1",
                        sound="buzzer")),
            data=data,
            token=token
        )
        response = messaging.send(message)
        logger.info(f"FCM Single Push Sent Successfully | Message ID: {response}")
        return True
    except Exception as e:
        logger.error(f"FCM Single Push Failed | Error: {e}")
        return False

#   ==========  Send Push Notification to Multiple Devices  ==========
def send_fcm_notification_multiple(payload:dict):
    """
      Send FCM Notification
      
    """
    logger.info(f"FCM Payload :: {payload}")
    token = payload.get("token")
    title = payload.get("title")
    body = payload.get("body")
    data = payload.get("data", {})
    logger.info(f"FCM Token :: {token}, Title :: {title}, Body :: {body}, Data :: {data}")
    if not token:
        logger.warning("FCM Token not found")
        return False
    try:
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body),
            token=token
        )
        response = messaging.send_multicast(message)
        logger.info(f"FCM Multiple Push Sent Successfully | Message ID: {response}")
        return response
    except Exception as e:
        logger.error(f"FCM Multiple Push Failed | Error: {e}")
        return False

    
#   ==========  Send Push Notification Asynchronously  ==========
def send_fcm_notification_async(payload: dict):
    try:
        if not payload.get("token"):
            logger.warning("FCM Token not found")
            return False

        fcm_executor.submit(send_fcm_notification, payload)

        logger.info("FCM Async task submitted successfully")

        return True

    except Exception as e:
        logger.error(f"FCM Async Push Failed | Error: {e}")
        return False


#  ===========   Send push Notification For Multiple Devices  ========== 
def send_bulk_notification(payload: dict):
    """
      Send FCM Notification
      
    """
    logger.info(f"FCM Payload :: {payload}")
    tokens = payload.get("tokens")
    title = payload.get("title")
    body = payload.get("body")
    logger.info(f"FCM Token :: {tokens}, Title :: {title}, Body :: {body}")
    if not tokens:
        logger.warning("FCM Token not found")
        return False
    message = messaging.MulticastMessage(
        notification= messaging.Notification(
            title=title,
            body=body
        ),
        token=tokens        
        
    )
    response = messaging.send_multicast(message)
    logger.info(f"FCM Multiple Push Sent Successfully | Message ID: {response}")
    return response