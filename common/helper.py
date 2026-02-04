
# logger = logging.getLogger(__name__)

from datetime import datetime, timedelta, timezone
import uuid

import jwt
from JWTAuth.models import UserToken
from common.models import DomainLookup
from constants import DB_STRF_TIME_FORMAT, DEFAULT_TIMEDIFF
from utils.common import get_parameter_value_by_key


class generalUtilities:
    def __init__(self,logger):
        self.logger = logger
        self.header_Token = None
        self.logger.info("General Utilities Initialized")
    def get_domainvalue_by_domaintype(self,domain_type):
        getdomain_data = DomainLookup.objects.filter(domain_type__in=domain_type,status=1).order_by("domain_value").values("domain_id","domain_type","domain_value","domain_code")
        result={}
        for i in range(len(domain_type)):
            result[f'{domain_type[i]}'] = list(filter(lambda x:x["domain_type"] == domain_type[i],getdomain_data))
        return result
    
    def get_token_timedelta_unit(self,**kwargs):
        try:
            """ Fetch Token Timedelta Unit  """
            timedelta_unit = kwargs.get("timeDeltaUnit","Minutes")
            time_delta = kwargs.get("timeDelta",DEFAULT_TIMEDIFF)
            timedelta_switcher={
                "Minutes":timedelta(minutes=time_delta),
                "Hours":timedelta(hours=time_delta),
                "Days":timedelta(days=time_delta)
            }
            return timedelta_switcher.get(timedelta_unit,timedelta(minutes=time_delta))
        except Exception as e:
            self.logger.exception(e)
            return e 
    
    def generate_new_authentication_token(self,**kwargs):
        """   
         Returns User specific authentication token
         UserId = user id and user type 

        """
        try:
            user_id = kwargs.get("user_id",None)
            user_type = kwargs.get("user_type",None)
            c_mob_no = kwargs.get("cMobNo",None)
            self.user_id,self.user_type,self.c_m_no = user_id,user_type,c_mob_no
            reqParam = ["jwt_algo","jwt_secret","token_expire_time","token_time_unit"]
            param_data = get_parameter_value_by_key(param_keys=reqParam)
            if param_data not in (None,""):
                algo = param_data["jwt_algo"]
                secret = param_data["jwt_secret"]
                expire_time_delta = int(param_data["token_expire_time"])
                token_time_unit = str(param_data["token_time_unit"])
            time_delta_var = self.get_token_timedelta_unit(timeDeltaUnit=token_time_unit,timeDelta=expire_time_delta)
            
            if self.user_type in (1,2):
                self.logger.info("Expire Time Delta [Admin] : {expire_time_delta}")
                payload={
                    "user_id":self.user_id,
                    "user_type":self.user_type,
                    "c_m_no":self.c_m_no,
                    "exp":datetime.now(timezone.utc) + time_delta_var,
                    "iat":datetime.now(timezone.utc)
                }
            elif self.user_type in (8,3):
                self.logger.info("Expire Time Delta [Citizen] : {expire_time_delta}")
                
                payload={
                    "user_id":self.user_id,
                    "user_type":self.user_type,
                    "c_m_no":self.c_m_no,
                    "exp":datetime.now(timezone.utc) + time_delta_var,
                    "iat":datetime.now(timezone.utc)
                }
            jwt_token = jwt.encode(payload=payload,key=secret,algorithm=algo)
            token_id_exists  = UserToken.objects.filter(
                user_id=self.user_id,
                user_type=self.user_type,
                c_m_no=self.c_m_no).exists()
            if token_id_exists:
                token_update_data={
                    "token":jwt_token,
                    "expiry_time":payload["exp"].strftime(f'{DB_STRF_TIME_FORMAT}'),
                    "updated_on":datetime.now(tc = timezone.utc).strftime(f'{DB_STRF_TIME_FORMAT}'),
                    "allow_flag":1
                }
                UserToken.objects.filter(
                    user_id=self.user_id,
                    user_type=self.user_type,
                    c_m_no=self.c_m_no
                    ).update(**token_update_data)
                self.logger.warning(f"Refresh token updated for respective User and User Type : {self.user_type} ")
            else:
                user_data = {
                    "user_id":self.user_id,
                    "user_type":self.user_type,
                    "c_m_no":self.c_m_no,
                    "token":jwt_token,
                    "expiry_time":payload["exp"].strftime(f'{DB_STRF_TIME_FORMAT}'),
                    "updated_on":datetime.now(tc = timezone.utc).strftime(f'{DB_STRF_TIME_FORMAT}'),
                    "allow_flag":1
                }
                UserToken.objects.create(**user_data)
            self.logger.warning(f"Refresh token created for respective User and User Type : {self.user_type} ")
            return jwt_token
        except Exception as e:
            self.logger.exception(e)
            return None
    def generate_request_code(self,requestType):
        if requestType == 1:
            return "S-"+str(uuid.uuid4())
        elif requestType == 2:
            return "C-"+str(uuid.uuid4())
        else:
            return None
            
            
                
                
                
                
                
                
                
            
                
            
            
    
        
        