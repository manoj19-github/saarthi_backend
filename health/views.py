from rest_framework.decorators import api_view
from rest_framework.response import (Response)
from rest_framework.status import (HTTP_200_OK)
from django.http import (JsonResponse)
from django.db import connections
from datetime import (datetime)
from errorcodes import (SUCCESSMESSAGE,CODE,DATA,ERROR,EXCEPTION,MESSAGE,SUCCESSCODE,TOKEN)
from constants import (DB_ALIAS_MASTER,DB_ALIAS_REPLICA)
import logging,gc

logger = logging.getLogger(__name__)



def HealthCheck(request):
    logger.warning('================================== START - Application Health =================================')
    sysTimeNow = datetime.now().strftime('%d-%m-%Y, %I:%M:%S.%f %p')
    logger.info(f'backend system local time now: {sysTimeNow}')
    output = {
        CODE:SUCCESSCODE,
        "TIME":sysTimeNow,
        "Conditions":"ok",
        "DjangoApp":"Generic Backend Service Health Check API",
        MESSAGE:SUCCESSMESSAGE,
        "DatabaseStatus":"Not Connected"
    }
    
    with connections[DB_ALIAS_MASTER].cursor() as cursor:
        cursor.execute("SELECT current_timestamp;")
        db_time = cursor.fetchone()
    output["DatabaseStatus"]="Connected"
    output["DatabaseTime"]=db_time[0]
    logger.info(f'backend system database time now: {db_time[0]}')
    logger.info('================================== END - Application Health =================================')
    return JsonResponse(output, status=HTTP_200_OK)