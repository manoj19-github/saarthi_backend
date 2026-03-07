
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
    
   

    def generate_new_authentication_token(self, **kwargs):
        """
        Generate JWT authentication token for user
        """
        try:
            # -----------------------------
            # Extract inputs
            # -----------------------------
            user_id = kwargs.get("user_id")
            user_type = kwargs.get("user_type")
            c_mob_no = kwargs.get("cMobNo")
            print("user_id",user_id)
            print("user_type",user_type)
            if not user_id or not user_type:
                raise ValueError("User ID or User Type not found")

            

            self.user_id = user_id
            self.user_type = user_type
            self.c_m_no = c_mob_no

            # -----------------------------
            # Fetch JWT config
            # -----------------------------
            reqParam = [
                "jwt_algo",
                "jwt_secret",
                "token_expire_time",
                "token_time_unit"
            ]
            param_data = get_parameter_value_by_key(param_keys=reqParam)

            if not param_data:
                raise ValueError("JWT configuration not found")

            algo = param_data["jwt_algo"]
            secret = param_data["jwt_secret"]
            expire_time_delta = int(param_data["token_expire_time"])
            token_time_unit = str(param_data["token_time_unit"])

            # -----------------------------
            # Token expiry calculation
            # -----------------------------
            time_delta_var = self.get_token_timedelta_unit(
                timeDeltaUnit=token_time_unit,
                timeDelta=expire_time_delta
            )

            now = datetime.now(timezone.utc)

            # -----------------------------
            # Payload (common for all users)
            # -----------------------------
            payload = {
                "user_id": self.user_id,
                "user_type": self.user_type,
                "c_m_no": self.c_m_no,
                "iat": now,
                "exp": now + time_delta_var
            }

            # -----------------------------
            # Create JWT token
            # -----------------------------
            jwt_token = jwt.encode(payload, secret, algorithm=algo)

            # -----------------------------
            # Save / Update token in DB
            # -----------------------------
            token_data = {
                "token": jwt_token,
                "expiry_time": payload["exp"].strftime(DB_STRF_TIME_FORMAT),
                "updated_on": now.strftime(DB_STRF_TIME_FORMAT),
                "allow_flag": 1
            }

            qs = UserToken.objects.filter(
                user_id=self.user_id,
                user_type=self.user_type,
                c_m_no=self.c_m_no
            )

            if qs.exists():
                qs.update(**token_data)
                self.logger.info(
                    f"Token updated for user_type {self.user_type}"
                )
            else:
                token_data.update({
                    "user_id": self.user_id,
                    "user_type": self.user_type,
                    "c_m_no": self.c_m_no
                })
                UserToken.objects.create(**token_data)
                self.logger.info(
                    f"Token created for user_type {self.user_type}"
                )

            return jwt_token

        except Exception as e:
            print("Exception in JWT generation",e)
            self.logger.exception("JWT generation failed")
            return None

    def generate_request_code(self,requestType):
            if requestType == 1:
                return "S-"+str(uuid.uuid4())
            elif requestType == 2:
                return "C-"+str(uuid.uuid4())
            else:
                return None
                
                
                    
                    
                    
                    
                    
                    
                    
            
                
            
            
    
        
        