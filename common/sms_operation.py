
import logging,json,requests
from django.conf import settings

logger = logging.getLogger(__name__)

def callSMSUrl(msg,mobile_no,temid):
    SMS_API_URL = getattr(settings,'SMS_API_URL',None)
    SMS_API_KEY = getattr(settings,'SMS_API_KEY',None)
    SMS_SENDER_ID = getattr(settings,'SMS_SENDER_ID',None)
    SMS_ENTITY_ID = getattr(settings,'SMS_ENTITY_ID',None)
    if not SMS_API_URL  or not SMS_API_KEY or not SMS_SENDER_ID or not SMS_ENTITY_ID:
        logger.error("SMS API URL, API KEY, SENDER ID and ENTITY ID are required for SMS Operation")
        return False
    payload = {
        "key":SMS_API_KEY,
        "from":SMS_SENDER_ID,
        "to":[str(mobile_no)],
        "body":str(msg),
        "templateid":str(temid),
        "entityid":SMS_ENTITY_ID
    }
    headers={
        "Content-Type":"application/json"
    }
    logger.warning(f"Request URL :: {SMS_API_URL}")
    logger.warning(f"Payload :: {payload}")
    response = requests.post(SMS_API_URL,data=json.dumps(payload),headers=headers)
    resp = response.json()
    logger.info(f"API Call Response :: {resp}")
    if response.status_code == 200:
        return True
    return False
    