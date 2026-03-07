import datetime
import logging
import random
import re
from time import time

from common.models import ParameterMaster
from constants import FIXED_OTP
from utils.constants import DOB_REGEX, EMAIL_REGEX, PHONE_REGEX

logger = logging.getLogger(__name__)

#  ============== Email validation Function     =================== 

def validate_email(email):
    try:
        email_flag = False
        email_regex = re.compile(EMAIL_REGEX)
        if re.fullmatch(email_regex, str(email)):
            email_flag = True
        else:
            email_flag = False
            raise Exception("Invalid Email")
    except Exception as e:
        logger.exception(e)
    finally:
        return email_flag
        
# ============== Phone number validation Function ===============
def validate_phone(phone):
    try:
        phone_flag = False
        phone_regex = re.compile(PHONE_REGEX)
        if re.fullmatch(phone_regex, str(phone)):
            phone_flag = True
        else:
            phone_flag = False
            raise Exception("Invalid Phone Number")
    except Exception as e:
        logger.exception(e)
    finally:
        return phone_flag
        

#   ======== Get Domain Value ======================

def get_domain_value_by_domain_type(request):
    pass

#  =============== Get the parameter from parameter key =================== 

def get_parameter_value_by_key(param_keys):
    result={}
    return_data= ParameterMaster.objects.filter(parameter_key__in=param_keys)
    for i in range(len(param_keys)):
        element = list(filter(lambda x:x["parameter_key"] == param_keys[i], return_data.values()))
        result[element[0]["parameter_key"]] = element[0]["parameter_value"]
    return result

    
#   Global Generate OTP Function
def generate_otp(otp_flag:int):
    if otp_flag == 1:
        return str(random.randint(100000,999999))
    else:
        otp_params = None
        otp_params = get_parameter_value_by_key(param_keys=["fixed_otp"])
        fixed_otp = otp_params.get("fixed_otp",FIXED_OTP)
        return fixed_otp if fixed_otp not in (None,"") else FIXED_OTP
    
def to_am_pm(time_value):
    if not time_value:
        return None
    if isinstance(time_value,datetime):
        dt = time_value
    elif isinstance(time_value,time):
        dt = datetime.combine(datetime.today(),time_value)
    elif isinstance(time_value,str):
        try:
            if "T" in time_value:
                dt = datetime.fromisoformat(time_value.replace("Z","+00:00"))
            else:
                dt = datetime.strptime(time_value,"%H:%M:%S")
        except ValueError:
            dt = datetime.strptime(time_value,"%H:%M")
    else:
        return None
    return dt.strftime("%I:%M %p").lstrip("0")
    
def validate_dob(dob):
    """Validate An Date Of Birth"""
    try:
        dob_flag = False
        dob_regex = re.compile(DOB_REGEX)
        if re.fullmatch(dob_regex, str(dob)):
            logger.info("This is an Perfect Date Of Birth Format")
            dob_flag = True
        else:
            dob_flag = False
            raise Exception(" No Date of Birth Format Matched With Respective Pattern")
    except Exception as e:
        logger.exception(e)
    finally:
        return dob_flag