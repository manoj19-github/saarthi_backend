from datetime import datetime, timedelta, timezone
from threading import Thread
import logging,time,secrets
from django.core.handlers.exception import AlreadySentOtpException, MandatoryInputMissingException, NoOTPExistsException
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import connection, transaction
from django.db.models import Q
from JWTAuth.models import FcmToken
from citizen.models import Citizen, LoginActivity
from citizen.raw_sql import citizen_details_query
from common.email_operation import send_mail
from common.helper import generalUtilities
from common.models import DomainLookup, SMSTemplate, UserOTP
from common.sms_operation import callSMSUrl
from common.utils import queryFetcherFn
from constants import ACTIVE, EXPIRED, INACTIVE, OPS_STRF_TIME_FORMAT
from errorcodes import SUCCESSCODE, SUCCESSMESSAGE
from users.models import User
from utils.common import generate_otp, get_parameter_value_by_key, validate_email, validate_phone
from utils.decorators import ratelimit_with_ip_whitelist, require_post, validate_form
from utils.exceptions import InvalidOTPException, OTPExpiredException, UserNotFoundException
from utils.formValidator import LoginForm, OTPGenerateForm


logger = logging.getLogger(__name__)

@csrf_exempt
@require_post
@validate_form(OTPGenerateForm)
@ratelimit_with_ip_whitelist(rate='5/m', method='POST')
def citizenOTPGenerate(request):
    """
    Generate OTP for citizen
    """
    logger.warning("Citizen OTP Generation API initiated")
    otp_update_data,response,previousEntryFlag,isSent,otpCreatedData = {},{},False,False,{}
    payload = request.data
    logger.info(f"Payload received for OTP generation: {payload}")
    username = payload.get('username',None)
    if username in (None,""):
        raise Exception("Mobile no or Email is required for OTP generation")
    
    # Validate mobile no or email
    if not validate_email(username) and not validate_phone(username):
        raise Exception("Invalid mobile no or email")
    
    reqParam = ["otp_validity","otp_flag","sms_flag","email_flag"]
    param_data = get_parameter_value_by_key(param_keys=reqParam)
    logger.info(f"Parameter data fetched: {param_data}")
    if param_data not in (None,""):
        otp_validity = int(param_data.get("otp_validity",5))
        otp_flag = int(param_data.get("otp_flag",1))
        sms_flag = int(param_data.get("sms_flag",1))
        email_flag = int(param_data.get("email_flag",1))
    if otp_validity in (None,""):
        raise Exception("OTP validity parameter is missing")
    
    #  ============== Wait for Next OTP Generation if previous OTP is still valid ==============
    wait_time_duratuion = int(otp_validity/2)
    otp = generate_otp(otp_flag = otp_flag)
    logger.info(f"Generated OTP: {otp}")
    currentDateTime = datetime.now(timezone.utc)
    timeNow = timezone.now()
    logger.info(f"Current DateTime in UTC Now: {currentDateTime} and TimeNow: {timeNow}")
    otp_details = list(UserOTP.objects.filter(
        Q(u_phone = username) | Q(u_email = username)
    )).exclude(otp__in=["USED","EXPIRED"]).order_by("-otp_id")[:1].values(
        "otp_id",
        "otp",
        "expiry_time",
        "created_on",
        "otp_lock_time"
    )
    logger.info(f"OTP Details: {otp_details} and length - {len(otp_details)}")
    
    if len(otp_details) > 0:
        logger.warning(f"Previous OTP Entry Found  :: {otp_details[0]} ")
        previousEntryFlag = True
        otp_id = otp_details[0]["otp_id"]
        otp = otp_details[0]["otp"]
        otp_time = otp_details[0]["created_on"]
        otp_lock_time = otp_details[0]["otp_lock_time"]
        expiry_time = otp_details[0]["expiry_time"]
        formatted_expiry_time = datetime.strftime(expiry_time,f'{OPS_STRF_TIME_FORMAT}')
        strf_otp_lock_time = datetime.strftime(expiry_time,f'{OPS_STRF_TIME_FORMAT}')
        validationTime = datetime.now(timezone.utc).strftime(f'{OPS_STRF_TIME_FORMAT}')
        logger.warning(f"OTP :: {otp} and OTP TIME :: {otp_time} and OTP LOCK TIME :: {otp_lock_time} and EXPIRY TIME :: {formatted_expiry_time}")
        
        # =============== Checking OTP Validation Time ============== 
        if validationTime > expiry_time:
            logger.warning("!!!!   OTP Expired !!!!")
            otp_update_data["otp"] = EXPIRED
            otp_update_data["updated_on"] = datetime.now(timezone.utc)
            expiry_time = currentDateTime + timedelta(minutes=int(otp_validity))
            otp_lock_time = currentDateTime + timedelta(minutes = wait_time_duratuion)
            
            otp_create_data={
                "otp":otp,
                "created_on":datetime.strftime(currentDateTime,'%Y-%m-%d %H:%M:%S'),
                "updated_on":datetime.strftime(currentDateTime,'%Y-%m-%d %H:%M:%S'),
                "expiry_time":datetime.strftime(expiry_time,'%Y-%m-%d %H:%M:%S'),
                "otp_lock_time":datetime.strftime(otp_lock_time,'%Y-%m-%d %H:%M:%S'),
                "updated_on":datetime.now(timezone.utc).strftime(f'{OPS_STRF_TIME_FORMAT}'),
            }
            if validate_phone(username):
                otp_create_data["u_phone"] = username
                otp_create_data["otp_type"] = 1
            else:
                otp_create_data["u_email"] = username
                otp_create_data["otp_type"] = 2
            logger.info(f"OTP Create Data: {otp_create_data}")
        else:
            logger.warning("Previous OTP is still valid")
            if validationTime < strf_otp_lock_time:
                is_sent = True
            else:
                otp_lock_time = otp_lock_time+timedelta(minutes=int(wait_time_duratuion))
                otp_update_data["otp_lock_time"] = datetime.strftime(otp_lock_time,'%Y-%m-%d %H:%M:%S')
                otp_update_data["updated_on"] = datetime.now(timezone.utc).strftime(f'{OPS_STRF_TIME_FORMAT}')
    else:
        logger.warning(" No previous OTP Entry Found")
        expiry_time = currentDateTime + timedelta(minutes=int(wait_time_duratuion))
        otp_lock_time = currentDateTime + timedelta(minutes = wait_time_duratuion)
        otp_create_data={
            "otp":otp,
            "created_on":datetime.strftime(currentDateTime,'%Y-%m-%d %H:%M:%S'),
            "expiry_time":datetime.strftime(expiry_time,'%Y-%m-%d %H:%M:%S'),
            "otp_lock_time":datetime.strftime(otp_lock_time,'%Y-%m-%d %H:%M:%S'),
        }
        if validate_phone(username):
            otp_create_data["u_phone"] = username
            otp_create_data["otp_type"] = 1
        else:
            otp_create_data["u_email"] = username
            otp_create_data["otp_type"] = 2
        logger.info(f"OTP Create Data: {otp_create_data}")
        
        #   -------------- Database Operations ---------------
        with transaction.atomic():
            logger.warning("Atomic Transaction Started")
            if previousEntryFlag and len(otp_details) > 0:
                UserOTP.objects.filter(otp_id=otp_id).update(**otp_update_data)
                logger.info("Previous OTP Entry Updated")
            if len(otp_create_data) > 0:
                UserOTP.objects.create(**otp_create_data)
                logger.info("New OTP Entry Created")
            logger.warning("Atomic Transaction Ended")
        
        #   -------------- Send OTP to Mobile No. ---------------
        if is_sent:
            lock_time_duration = otp_lock_time - timeNow
            if lock_time_duration.seconds > 60 : 
                lock_time_duration = str(int(lock_time_duration.seconds/60))
            else:
                lock_time_duration = str(lock_time_duration.seconds) + " Seconds"
            raise AlreadySentOtpException(f"OTP already sent to {username} in {lock_time_duration}")
        
        #  ============================================== 
        #   OTP SMS & Email Sent
        # =============================================
        logger.info(f"userNameFormat :: {username}")
        
        if validate_phone(username):
            logger.info(f"SMS Flag  should be 1 to send sms :: sms_flag = {sms_flag}")
            if sms_flag == 1:
                logger.info(f"Sending OTP to {username} via SMS")
                msg_body = SMSTemplate.objects.filter(template_key="OTP_LOGIN",is_active=True).first().message_body.format(otp=str(otp),expiry_time = str(otp_validity)) 
                temp_id = SMSTemplate.objects.filter(template_key="OTP_LOGIN",is_active=True).first().template_id
                
                if msg_body is not None and username not in (None,""):
                    logger.info(f"Attempting to send OTP to {username} via SMS :: {username}")
                    Thread(target=callSMSUrl,args=(msg_body,str(username),temp_id,)).start()
                else:
                    logger.warning("No message sent this time as message body is empty")
            else:
                logger.warning("SMS Flag is 0 so no SMS sent")
        else:
            logger.warning("Invalid mobile no or email")
    
    #   --------------- Sent OTP to Email ---------------
    if validate_email(username):
        logger.info(f"Sending OTP to {username} via Email")
        if email_flag == 1:
            logger.info(f"Attempting to send OTP to {username} via Email :: {username}")
            subject = "OTP for Email verification"
            context = {
                "otp":otp,
                "expiry_time":str(otp_validity)
            }
            email_body = render_to_string("email_otp_tem",context)
            logger.info(f"Email Body :: {email_body}")
            email_args = {
                "subject":subject,
                "body":email_body,
                "to":str(username),
            }
            
            #  ---------------- Send OTP to Email ---------------
            Thread(target=send_mail,args=(email_args)).start()
            logger.info(f"OTP sent to {username} via Email")
        else:
            logger.warning("Email Flag is 0 so no Email sent")
    else:
        logger.warning("Invalid mobile no or email")
    response["message"] = "OTP Sent"
    return JsonResponse(response)

@csrf_exempt
@require_post
@validate_form(LoginForm)

def citizenLogin(request):
    """
    Login for citizen
    """
    logger.warning("Citizen Login API initiated")
    otp_update_data,response,dataset,user_id,token,device_type,user_type = {},{},None,None,None,{},None,1
    genUtil = generalUtilities(logger)
    payload = request.data
    logger.info(f"Payload received for Login : {payload}")
    username = payload.get('username',None)
    otp = payload.get('otp',None)
    fcm_token = payload.get('fcm_token',None)
    logger.info(f"Username : {username} and OTP : {otp} and FCM Token : {fcm_token}")
    if username in (None,"") or otp in (None,""):
        raise MandatoryInputMissingException("Username or OTP is missing")
    logger.info("Username Format Checking .....")
    if not validate_phone(phone =username) or not validate_email(email = username):
        raise Exception("Invalid mobile no or email")
    
    #  Check if an OTP exists for the given email or mobile no
    otp_exists = list(UserOTP.objects.filter(
        Q(u_phone = username) | Q(u_email = username)
    ))
    logger.info(f"OTP Exists for the given mobile no or email : {otp_exists}")
    if len(otp_exists) <= 0:
        raise NoOTPExistsException("No OTP exists for the given mobile no or email")
    otp_entry = otp_exists[0]
    otp_id = otp_entry.otp_id
    saved_otp = otp_entry.otp
    expiry_time = otp_entry.expiry_time
    
    #  Convert date time to string format 
    expiry_time_str = expiry_time.strftime(f'{OPS_STRF_TIME_FORMAT}')
    validation_time = datetime.now(timezone.utc).strftime(f'{OPS_STRF_TIME_FORMAT}')
    otp_update_data["updated_on"] = datetime.now(timezone.utc).strftime(f'{OPS_STRF_TIME_FORMAT}')  
    logger.warning("OTP :: {saved_otp} || EXPIRY TIME :: {expiry_time_str} || VALIDATION TIME :: {validation_time}")
    
    #  ============== Check if OTP is Expired or not ==============
    if validation_time >=  expiry_time_str:
        logger.warning("!!!!   OTP Expired !!!!")
        otp_update_data["otp"] = EXPIRED
        
        #   ===============  Update OTP in the Database =============== 
        with transaction.atomic():
            logger.warning("Atomic Transaction Started")
            UserOTP.objects.filter(otp_id=otp_id).update(**otp_update_data)
            logger.warning("Atomic Transaction Ended")
            logger.info("OTP successfully marked as expired")
        raise OTPExpiredException("OTP Expired")
    logger.info(f"OTP check | {otp} fetching user data please wait .......")
    if  saved_otp != otp:
        raise InvalidOTPException("Invalid OTP")
    logger.info(f"OTP Matched | {otp} => {saved_otp} | Fetching User Data  please wait ......")
    logger.warning(f"OTP Matched , marking OTP as USED")
    otp_update_data["otp"] = "USED"
    
    with transaction.atomic():
        logger.warning("Atomic Transaction Started")
        UserOTP.objects.filter(otp_id=otp_id).update(**otp_update_data)
        logger.warning("Atomic Transaction Ended")
        logger.info("OTP successfully marked as USED")
    
    #  ------------   User Existence Validation   ----------- 
    citizen_user_type = DomainLookup.objects.filter(domain_type="user_type",domain_value="Citizen").values_list("domain_code",flat=True).first()
    user_data_set=User.objects.filter(Q(phone=username) | Q(email=username) , is_active=True,user_type=citizen_user_type)
    if user_data_set.exists():
        user = user_data_set.get()
        user_id = user.id
        ref_id = user.ref_id
        c_m_no = user.c_m_no
        user_type = user.user_type
        logger.info(f"User Existence Validation | User Found | {user}")
        
        #   ==============  Citizen Data return ================= 
        citizen_data_set = Citizen.objects.filter(id = ref_id,status=ACTIVE)
        if citizen_data_set.exists():
            citizen = citizen_data_set.first()
            citizen_id = citizen.id if citizen else None
            logger.info(f"Citizen ID ::: {citizen_id}")
            
            # ============   Database connection =============
            with connection.cursor() as cursor:
                query = citizen_details_query(citizen_id)
                logger.info(f"Citizen Query :: {query}")
                #   Query Execution 
                dataset = queryFetcherFn(query,cursor)
                logger.info(f"Citizen Dataset :: {dataset}")
            
            #   ==============  Token Generation =================
            token_user_type = DomainLookup.objects.filter(domain_type="user_type",domain_value="Citizen").values_list("domain_code",flat=True).first()  or user_type
            token = genUtil.generate_new_authentication_token(userId=user_id,cMobNo=username,userType=token_user_type)
            logger.info(f"Token Generated :: {token} and Token User Type :: {token_user_type}")
            
            if token is not (None,""):
                if LoginActivity.objects.filter(m_no=username,active_status=ACTIVE).exists():
                    LoginActivity.objects.filter(m_no=username,active_status=ACTIVE).update(active_status=INACTIVE,logout_time=datetime.now(timezone.utc).strftime(f'{OPS_STRF_TIME_FORMAT}'),updated_on=datetime.now(timezone.utc).strftime(f'{OPS_STRF_TIME_FORMAT}'))
                    logger.info(f"Previous Citizen Login Activity Record Found and Updated")
                LoginActivity.objects.create(m_no=username,user_type=user_type,login_time=datetime.now(timezone.utc).strftime(f'{OPS_STRF_TIME_FORMAT}'),logout_time=None,active_status=ACTIVE,created_on=datetime.now(timezone.utc).strftime(f'{OPS_STRF_TIME_FORMAT}'))
                
                #  ======================  FCM Token Generation   ====================
                
                logger.info(f"FCM Token :: {fcm_token} , Token user type :: {token_user_type}")
                
                if FcmToken.objects.filter(user_id=user_id,user_type=token_user_type).exxists():
                    FcmToken.objects.filter(user_id=user_id,user_type=token_user_type).update(token=fcm_token,c_m_no=username,device_type=device_type,updated_by=user_id,updated_on=datetime.now(timezone.utc).strftime(f'{OPS_STRF_TIME_FORMAT}'),is_active=ACTIVE)
                    logger.info(f"FCM Token Updated for respective User and User Type : {token_user_type} ")
                else:
                    FcmToken.objects.create(
                        user_id = user_id,
                        user_type = token_user_type,
                        token=fcm_token,
                        device_type=device_type,
                        c_m_no=username,
                        created_by=user_id,
                        created_on=datetime.now(timezone.utc).strftime(f'{OPS_STRF_TIME_FORMAT}'),
                        updated_by=user_id,
                        is_active=ACTIVE
                    )
                    logger.info(f"FCM Token Created for respective User and User Type : {token_user_type} ")
                    
                    request.auth_token = token
                    response["citizen_data"] = len(dataset) > 0 and dataset[0] or None
                    response['citizen_data']['user_id'] = user_id
                    response = response
                    response['Code'] = SUCCESSCODE
                    response['Message'] = SUCCESSMESSAGE
            else:
                raise UserNotFoundException("User Not Found")
    
    #  If User not found             #    
    
    else:
        response={
            "citizen_data":{
                "user_id":user_id    
            },
        }
        response = response 
    response['Code'] = SUCCESSCODE
    return JsonResponse(response)
                
                
                
                
        
    
            
        
    
        
        
        
    
    
    
            
            
            
                    
                    
                    
                
                
    
        
            
                
                
                
            
            
        
    
    
    
    
    
    
    

    
    
    
    
    
    
    
    