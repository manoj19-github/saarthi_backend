from datetime import datetime, timedelta
import json
from django.forms import model_to_dict
from django.utils import timezone
from rest_framework.decorators import api_view
from threading import Thread
import logging,time,secrets

from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import connection, transaction
from django.db.models import Q
from JWTAuth.models import FcmToken
from citizen.models import Citizen, CitizenAddress, DeclineQuestionMaster, LoginActivity, ServiceRequest, ServiceRequestLifecycle
from citizen.raw_sql import citizen_details_query
from common.email_operation import send_mail
from common.firebase import send_fcm_notification_async
from common.helper import generalUtilities
from common.models import Block, District, DomainLookup, FcmNotification, SMSTemplate, Sector, Services, State,UserOtp
from common.sms_operation import callSMSUrl
from common.utils import queryFetcherFn
from constants import ACTIVE, DB_STRF_TIME_FORMAT, EXPIRED, INACTIVE, OPS_STRF_TIME_FORMAT, STATUS_2, STATUS_2_MESSAGE, STATUS_3, STATUS_3_MESSAGE, STATUS_4, STATUS_4_MESSAGE, STATUS_5, STATUS_5_MESSAGE, STATUS_6, STATUS_6_MESSAGE, STATUS_7, STATUS_7_MESSAGE, STATUS_8, STATUS_9, STATUS_9_MESSAGE, TITLE
from errorcodes import SUCCESSCODE, SUCCESSMESSAGE
from gigworkers.models import Candidate
from users.models import User
from utils.common import generate_otp, get_parameter_value_by_key, validate_dob, validate_email, validate_name, validate_phone
from utils.decorators import ratelimit_with_ip_whitelist, require_post, validate_form
from utils.exceptions import AlreadySentOtpException, InvalidOTPException, InvalidUsernameFormatException, MandatoryInputMissingException, NoOTPExistsException, OTPExpiredException, UserNotFoundException
from utils.formValidator import CitizenServiceRequestForm, LoginForm, OTPGenerateForm, SignupForm
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .swagger_types import citizen_register_error_response,citizen_register_success_response,citizen_register_request_schema, otp_success_response, otp_error_response, otp_request_schema,citizen_login_error_response,citizen_login_success_response,citizen_login_request_schema

logger = logging.getLogger(__name__)



@swagger_auto_schema(
    method="post",
    request_body=otp_request_schema,
    responses={
        200: otp_success_response,
        400: otp_error_response,
        409: "OTP already sent",
    },
    tags=["Citizen Authentication"]
)
@csrf_exempt
@api_view(["POST"])
@require_post
@validate_form(OTPGenerateForm)
@ratelimit_with_ip_whitelist(rate="5/m", method="POST")
def citizenOTPGenerate(request):

    payload = request.data
    username = payload.get("username")

    if not username:
        raise MandatoryInputMissingException("Mobile or Email is required")

    if not validate_email(username) and not validate_phone(username):
        raise Exception("Invalid mobile or email")

    params = get_parameter_value_by_key([
        "otp_validity", "otp_flag", "sms_flag", "email_flag"
    ])

    otp_validity = int(params.get("otp_validity", 5))
    sms_flag = int(params.get("sms_flag", 1))
    email_flag = int(params.get("email_flag", 1))
    otp_flag = int(params.get("otp_flag", 1))

    now = timezone.now()
    otp = generate_otp(otp_flag)

    existing = UserOtp.objects.filter(
        Q(u_phone=username) | Q(u_email=username)
    ).exclude(otp__in=["USED", "EXPIRED"]).order_by("-otp_id").first()
    if existing and existing.expiry_time:
        expiry_time = existing.expiry_time
        
        if timezone.is_naive(expiry_time):
            expiry_time = timezone.make_aware(expiry_time)
        if expiry_time > now:
            raise AlreadySentOtpException("OTP already sent and still valid")
    # if existing and existing.expiry_time > now:
    #     raise AlreadySentOtpException("OTP already sent and still valid")

    expiry_time = now + timedelta(minutes=otp_validity)
    lock_time = now + timedelta(minutes=otp_validity // 2)

    with transaction.atomic():
        if existing:
            existing.otp = EXPIRED
            existing.updated_on = now
            existing.save()

        UserOtp.objects.create(
            otp=otp,
            u_phone=username if validate_phone(username) else None,
            u_email=username if validate_email(username) else None,
            otptype=1 if validate_phone(username) else 2,
            created_on=now,
            expiry_time=expiry_time,
            otp_lock_time=lock_time
        )

    # SMS
    if validate_phone(username) and sms_flag == 1:
        print("SMS Flag is True validate phone passed")
        template = SMSTemplate.objects.filter(
            template_key="OTP_LOGIN", is_active=True
        ).first()

        if template:
            msg = template.message_body.format(
                otp=otp, expiry_time=otp_validity
            )
            Thread(
                target=callSMSUrl,
                args=(msg, username, template.template_id)
            ).start()

    # EMAIL
    if validate_email(username) and email_flag == 1:
        print("email Flag is True validate email passed")
        body = render_to_string("email_otp_tem.html", {
            "otp": otp,
            "expiry_time": otp_validity
        })
        Thread(
            target=send_mail,
            args=({
                "subject": "OTP Verification",
                "body": body,
                "to": username
            },)
        ).start()

    return JsonResponse({"message": "OTP Sent"}, status=200)

@swagger_auto_schema(
    method="post",
    operation_summary="Citizen Login using OTP",
    operation_description="""
    Login API for Citizen using OTP authentication.

    - Accepts **mobile number or email**
    - Validates OTP
    - Returns citizen profile data
    - Registers FCM token
    """,
    request_body=citizen_login_request_schema,
    responses={
        200: citizen_login_success_response,
        400: citizen_login_error_response,
        401: "Invalid OTP",
        404: "User not found",
        410: "OTP expired",
        500: "Internal Server Error"
    },
    tags=["Citizen Authentication"]
)

@csrf_exempt
@api_view(["POST"])
@require_post
@validate_form(LoginForm)
def citizenLogin(request):
    """
    Login for citizen
    """
    logger.warning("Citizen Login API initiated")
    print("Citizen Login API initiated")
    otp_update_data,response,dataset,user_id,token,device_type,user_type = {},{},None,None,None,{},None
    genUtil = generalUtilities(logger)
    payload = request.data
    print("Payload received for Login : ",payload)
    logger.info(f"Payload received for Login : {payload}")
    username = payload.get('username',None)
    otp = payload.get('otp',None)
    fcm_token = payload.get('fcm_token',None)
    print("Username : ",username," and OTP : ",otp," and FCM Token : ",fcm_token)
    logger.info(f"Username : {username} and OTP : {otp} and FCM Token : {fcm_token}")
    if username in (None,"") or otp in (None,""):
        raise MandatoryInputMissingException("Username or OTP is missing")
    logger.info("Username Format Checking .....")
    if not validate_phone(phone =username) and not validate_email(email = username):
        raise Exception("Invalid mobile no or email")
    
    #  Check if an OTP exists for the given email or mobile no
    otp_exists = UserOtp.objects.filter(Q(u_phone=username) | Q(u_email=username)).order_by('-created_on')
    
    print(f"OTP Exists for the given mobile no or email : {len(otp_exists)}")
    logger.info(f"OTP Exists for the given mobile no or email : {otp_exists}")
    if len(otp_exists) <= 0:
        raise NoOTPExistsException("No OTP exists for the given mobile no or email")
    otp_entry = otp_exists[0]
    print(f"OTP Entry :: {otp_entry}")
    otp_id = otp_entry.otp_id
    saved_otp = otp_entry.otp
    expiry_time = otp_entry.expiry_time
    
    #  Convert date time to string format 
    expiry_time_str = expiry_time.strftime(f'{OPS_STRF_TIME_FORMAT}')
    validation_time = timezone.now().strftime(OPS_STRF_TIME_FORMAT)
    otp_update_data["updated_on"] = timezone.now().strftime(f'{OPS_STRF_TIME_FORMAT}')  
    logger.warning("OTP :: {saved_otp} || EXPIRY TIME :: {expiry_time_str} || VALIDATION TIME :: {validation_time}")
    
    #  ============== Check if OTP is Expired or not ==============
    if validation_time >=  expiry_time_str:
        logger.warning("!!!!   OTP Expired !!!!")
        otp_update_data["otp"] = EXPIRED
        
        #   ===============  Update OTP in the Database =============== 
        with transaction.atomic():
            logger.warning("Atomic Transaction Started")
            UserOtp.objects.filter(otp_id=otp_id).update(**otp_update_data)
            logger.warning("Atomic Transaction Ended")
            logger.info("OTP successfully marked as expired")
        raise OTPExpiredException("OTP Expired")
    logger.info(f"OTP check | {otp} fetching user data please wait .......")
    print("saved_otp",saved_otp," and otp",otp)
    print("saved_otp",saved_otp)
    if(saved_otp == "USED"):
        raise InvalidOTPException("OTP already used")           
    print("otp",otp)
    if  saved_otp != otp:
        raise InvalidOTPException("Invalid OTP")
    logger.info(f"OTP Matched | {otp} => {saved_otp} | Fetching User Data  please wait ......")
    logger.warning(f"OTP Matched , marking OTP as USED")
    otp_update_data["otp"] = "USED"
    
    with transaction.atomic():
        logger.warning("Atomic Transaction Started")
        UserOtp.objects.filter(otp_id=otp_id).update(**otp_update_data)
        logger.warning("Atomic Transaction Ended")
        logger.info("OTP successfully marked as USED")
    
    #  ------------   User Existence Validation   ----------- 
    citizen_user_type = DomainLookup.objects.filter(domain_type="user_type",domain_value="Citizen").values_list("domain_code",flat=True).first()
    user_data_set=User.objects.filter(Q(phone=username) | Q(email=username) , is_active=True,user_type=citizen_user_type)
    if user_data_set.exists():
        user = user_data_set.get()
        user_id = user.id
        ref_id = user.ref_id
        user_type = user.user_type
        logger.info(f"User Existence Validation | User Found | {user}")
        print(f"User Existence Validation | User Found | {user}")
        
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
                print("dataset",dataset)
            
            #   ==============  Token Generation =================
            token_user_type = DomainLookup.objects.filter(domain_type="user_type",domain_value="Citizen").values_list("domain_code",flat=True).first()  or user_type
            print("token_user_type",token_user_type)
            print("username",username)
            token = genUtil.generate_new_authentication_token(user_id=user_id,cMobNo=username,user_type=token_user_type)
            print("token-------------------------------------------",token)
            logger.info(f"Token Generated :: {token} and Token User Type :: {token_user_type}")
            
            if token  not in (None,""):
                updated = LoginActivity.objects.filter(m_no=username,active_status=ACTIVE).update(active_status=INACTIVE,logout_time=timezone.now().strftime(f'{DB_STRF_TIME_FORMAT}'),updated_on=timezone.now().strftime(f'{DB_STRF_TIME_FORMAT}'))
                print(f"FCM Token ::  276   {fcm_token} , Token user type :: {token_user_type}")
                LoginActivity.objects.create(m_no=username,user_type=user_type,login_time=timezone.now().strftime(f'{OPS_STRF_TIME_FORMAT}'),logout_time=None,active_status=ACTIVE,created_on=timezone.now().strftime(f'{OPS_STRF_TIME_FORMAT}'))
                
                #  ======================  FCM Token Generation   ====================
                
                logger.info(f"FCM Token :: {fcm_token} , Token user type :: {token_user_type}")
                print(f"FCM Token :: {fcm_token} , Token user type :: {token_user_type}")
                if FcmToken.objects.filter(user_id=user_id,user_type=token_user_type).exists():
                    FcmToken.objects.filter(user_id=user_id,user_type=token_user_type).update(token=fcm_token,c_m_no=username,device_type=device_type,updated_by=user_id,updated_on=timezone.now().strftime(f'{OPS_STRF_TIME_FORMAT}'),is_active=ACTIVE)
                    logger.info(f"FCM Token Updated for respective User and User Type : {token_user_type} ")
                    print(f"FCM Token Updated for respective User and User Type : {token_user_type} ")
                    # return JsonResponse(response,status=200)
                else:
                    FcmToken.objects.create(
                        user_id = user_id,
                        user_type = token_user_type,
                        token=fcm_token,
                        device_type=device_type,
                        c_m_no=username,
                        created_by=user_id,
                        created_on=timezone.now().strftime(f'{OPS_STRF_TIME_FORMAT}'),
                        updated_by=user_id,
                        is_active=ACTIVE
                    )
                logger.info(f"FCM Token Created for respective User and User Type :  298 ::  {token_user_type} ")
                print(f"FCM Token Created for respective User and User Type :  298 ::  {token_user_type} ")
                    
                response["auth_token"] = token
                response["citizen_data"] = len(dataset) > 0 and dataset[0] or None
                response['citizen_data']['user_id'] = user_id
                    # response = response
                response['Code'] = SUCCESSCODE
                response['Message'] = SUCCESSMESSAGE
                print("Response Data :: ",response)
                logger.info(f"Response Data :: {response}")
                return JsonResponse(response,status=200)
            else:
                raise UserNotFoundException("User Not Found")
    
    #  If User not found             #    
    
    else:
        raise UserNotFoundException("User Not Found")


@swagger_auto_schema(
    method="post",
    operation_summary="Citizen Registration",
    operation_description="""
    API to register or update a Citizen profile.

    **Features**
    - Registers new Citizen & User
    - Updates existing Citizen profile
    - Generates authentication token
    - Logs login activity

    **Logic**
    - If `citizen_id` & `user_id` are missing → New Registration
    - If present → Profile Update
    """,
    request_body=citizen_register_request_schema,
    responses={
        200: citizen_register_success_response,
        400: citizen_register_error_response,
        404: "User not found",
        409: "Mobile or Email already used",
        500: "Internal Server Error"
    },
    tags=["Citizen Registration"]
)

@csrf_exempt
@api_view(["POST"])
@require_post
@validate_form(SignupForm)
def citizenRegister(request):
    logger.warning("============== Citizen Registration API ==============")
    message,new_user_id,token,response=None,None,None,{}
    payload = request.data
    logger.info(f"Payload received for Register : {payload}")
    user_id = payload.get('user_id',None)
    citizen_id=payload.get('citizen_id',None)
    first_name=payload.get('first_name',None)
    middle_name=payload.get('middle_name',None)
    last_name=payload.get('last_name',None)
    gender=payload.get('gender',None)
    dob=payload.get('dob',None)
    mobile_no=payload.get('mobile_no',None)
    email=payload.get('email',None)
    state_id = payload.get('state_id',None)
    district_id = payload.get('district_id',None)
    block_id = payload.get('block_id',None)
    pincode = payload.get('pincode',None)
    genUtil = generalUtilities(logger)
    
    if not validate_phone(phone=mobile_no):
        raise InvalidUsernameFormatException("Invalid mobile no")
    
    if email in (None,"") or not validate_email(email=email):
        raise InvalidUsernameFormatException("Email is missing")
    if not validate_dob(dob=dob):
        raise InvalidUsernameFormatException("Invalid Date of Birth")
    
    #   State Data 
    stateDetails = State.objects.filter(id=state_id).first()
    districtDetails = District.objects.filter(id=district_id).first()
    blockDetails = None
    if block_id not in (None,''):
        blockDetails = Block.objects.filter(id=block_id).first()
    user_type = DomainLookup.objects.filter(domain_type="user_type",domain_value="Citizen").values_list("domain_code",flat=True).first()
    
    with transaction.atomic():
        if citizen_id in (None,""):
            if user_id in (None,""):
                citizen_data_details = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "date_of_birth": dob,
                    "mobile_number": mobile_no,
                    "email": email,
                    "state": stateDetails,
                    "district": districtDetails,
                    "block": blockDetails,
                    "pincode": pincode,
                    "user_type": user_type,
                    "created_by": user_id,
                        "created_on": timezone.now().strftime(f'{DB_STRF_TIME_FORMAT}'),
                    "updated_by": None,
                    "updated_on": timezone.now().strftime(f'{DB_STRF_TIME_FORMAT}'),
                }
                citizen = Citizen.objects.create(**citizen_data_details)
                citizen_id = citizen.id
                logger.info(f"Citizen Created with ID : {citizen_id}")
                
                
                #  =================== 
                #  User Data Validation
                # ===================== 
                
                if User.objects.filter(Q(phone__iexact=mobile_no) | Q(email__iexact=email)).exists():
                    raise InvalidUsernameFormatException("Mobile no or Email  already used")
                
                user_data_details = {
                    "username":" ".join(filter(None,[first_name,middle_name,last_name])),
                    "password": None,
                    "email": email,
                    "user_type": user_type,
                    "ref_id": citizen_id,
                    "phone": mobile_no,
                    "is_active": ACTIVE,
                    "created_on": timezone.now().strftime(f'{DB_STRF_TIME_FORMAT}'),
                    "updated_on": timezone.now().strftime(f'{DB_STRF_TIME_FORMAT}'),
                    "created_by": citizen_id,
                    "updated_by": None,
                }
                user = User.objects.create(**user_data_details)
                new_user_id = user.id
                print("new user id ",new_user_id)
                logger.info(f"User Created with ID : {new_user_id}")
                with connection.cursor() as cursor:
                    query = citizen_details_query(citizen_id)
                    dataset = queryFetcherFn(query,cursor)
            token_user_type = DomainLookup.objects.filter(domain_type="user_type",domain_value="Citizen").values_list("domain_code",flat=True).first() or user_type
            token = genUtil.generate_new_authentication_token(user_id=new_user_id,cMobNo=mobile_no,user_type=token_user_type)
            print("token",token)
            print("token_user_type",token_user_type)
            response = {
                    "registered_data": {
                        "citizen": dataset,
                        "user": model_to_dict(user),
                        
                    }
                }
        
            if token  not in (None,""):
                if LoginActivity.objects.filter(m_no=mobile_no,active_status=ACTIVE).exists():
                    LoginActivity.objects.filter(m_no=mobile_no,active_status=ACTIVE).update(active_status=INACTIVE,logout_time=timezone.now().strftime(f'{DB_STRF_TIME_FORMAT}'),updated_on=timezone.now().strftime(f'{DB_STRF_TIME_FORMAT}'))
                LoginActivity.objects.create(m_no=mobile_no,user_type=user_type,login_time=timezone.now().strftime(f'{DB_STRF_TIME_FORMAT}'),logout_time=None,active_status=ACTIVE,created_on=timezone.now().strftime(f'{DB_STRF_TIME_FORMAT}'))
                logger.info(f"Previous Citizen Login Activity Record Found and Updated")
                message = "Citizen Registered Successfully"
        else:
            if user_id not in (None,""):
                Citizen.objects.filter(id=citizen_id).update(first_name=first_name,last_name=last_name,gender=gender,dob=dob,mobile_number=mobile_no,email=email,state=stateDetails,district=districtDetails,block=blockDetails,pincode=pincode,user_type=user_type,updated_by=user_id,updated_on=timezone.now().strftime(f'{DB_STRF_TIME_FORMAT}'))
                logger.info(f"Citizen Data Updated")
                User.objects.filter(id=user_id).update(username=" ".join(filter(None,[first_name,middle_name,last_name])),password=None,email=email,user_type=user_type,ref_id=citizen_id,phone=mobile_no,is_active=ACTIVE,updated_on=timezone.now().strftime(f'{DB_STRF_TIME_FORMAT}'),updated_by=citizen_id)
                logger.info(f"User Data Updated")
                message = "Citizen Profile Updated Successfully"
                
                response = {
                    "registered_data": {
                        "citizen_id": citizen_id,
                        "user_id": user_id,
                        
                    }
                }
            else:
                raise UserNotFoundException("User Not Found")
        response["auth_token"] = token
        response["Code"] = SUCCESSCODE
        response["Message"] = message
        logger.warning(f"Citizen Registered Successfully")
        return JsonResponse(response,status=200)

@csrf_exempt
@api_view(["POST"])
@require_post
@validate_form(CitizenServiceRequestForm)
def citizenServiceRequest(request):
    logger.warning("============== Citizen Service Request API ==============")
    message,day_code = None,None
    payload = request.data
    logger.info(f"Payload : {payload}")
    
    service_request_id = payload.get('service_request_id',None)
    citizen_id = payload.get('citizen_id',None)
    candidate_id = payload.get("candidate_id",None)
    service_id = payload.get("service_id",None)
    address_id = payload.get("address_id",None)
    district_id = payload.get("district_id",None)
    service_status_to = payload.get("service_status_to",None)
    remarks = payload.get("remarks",None)
    preferred_day = payload.get("preferred_day",None)
    start_time = payload.get("start_time",None)
    end_time = payload.get("end_time",None)
    code = payload.get("code",None)
    question_id = payload.get("question_id",None)
    logger.info(f"payload >>>> {payload}  citizen id {citizen_id} candidate id {candidate_id} service id {service_id} district id {district_id} service status to {service_status_to} remarks {remarks} preferred day {preferred_day} start time {start_time} end time {end_time} code {code} question id {question_id}")
    
    current_datetime = datetime.now(timezone.utc).strftime(DB_STRF_TIME_FORMAT)
    citizen_address = CitizenAddress.objects.filter(id=address_id,status=ACTIVE).first()
    address_name  = " ".join(filter(None,[citizen_address.address_line_1,citizen_address.address_line_2]))
    ctizenDistrict = District.objects.filter(id=district_id,status=ACTIVE).first()
    citizen_details = Citizen.objects.filter(id=citizen_id,status=ACTIVE).first()
    citizen_name = " ".join(filter(None,[citizen_details.first_name,citizen_details.middle_name,citizen_details.last_name]))
    # citizen_user_type = DomainLookup.objects.filter(domain_type="user_type",domain_value="Citizen").values_list("domain_code",flat=True).first()
    citizen_user_id = User.objects.filter(id=citizen_id,user_type=citizen_user_type).values_list("id",flat=True).first()
    citizen_mobile_no = citizen_details.mobile_number
    service_details = Services.objects.select_related("skill").filter(id = service_id,status=ACTIVE)
    skill_details = getattr(service_details,"skill",None)
    skill_id = getattr(service_details,"skill_id",None)
    sector_details = Sector.objects.filter(id=skill_id,status=ACTIVE).first()
    candidate_details = Candidate.objects.filter(id=candidate_id,status=ACTIVE).first()
    candidate_name="Unknown User"
    if candidate_details is not None:
        candidate_name = " ".join(filter(None,[candidate_details.first_name,candidate_details.middle_name,candidate_details.last_name]))
    domain_data = DomainLookup.objects.filter(
        Q(domain_type="user_type") | 
        Q(domain_value_in=["Citizen","Gig Worker"]) | Q(domain_type="service_status",domain_code=service_status_to)
    ).values("domain_code","domain_value","domain_code")
    
    lookup = {f"{x['domain_code']}": x['domain_value'] for x in domain_data}
    
    citizen_user_type = lookup.get("user_type_Citizen")
    candidate_user_type = lookup.get("user_type_Gig Worker")
    status_name = next(
        (x['domain_value'] for x in domain_data if x['domain_type'] == "service_status"),
        None
    )
    fcm_data = FcmNotification.objects.filter(
        status=service_status_to,
        is_active=ACTIVE
    ).values("title", "notification").first()

    title = (fcm_data.get("title") if fcm_data else None) or TITLE
    notification = fcm_data.get("notification") if fcm_data else None
    candidate_tokens = FcmToken.objects.filter(user_id=candidate_id,is_active=ACTIVE).values_list("token",flat=True)
    candidate_user_id = User.objects.filter(ref_id=candidate_id,user_type=candidate_user_type).values_list("id",flat=True).first()
    tokens = FcmToken.objects.filter(Q(user_id = candidate_user_id) | Q(user_id=citizen_user_id),is_active=ACTIVE).values("user_id","token","user_type")
    tokens = FcmToken.objects.filter(
    Q(user_id=candidate_user_id, user_type=candidate_user_type) |
    Q(user_id=citizen_user_id, user_type=citizen_user_type),
    is_active=True
    ).values("user_id", "user_type", "token")

    token_map = {(t["user_id"], t["user_type"]): t["token"] for t in tokens}

    candidate_tokens = token_map.get((candidate_user_id, candidate_user_type))
    citizen_tokens = token_map.get((citizen_user_id, citizen_user_type))
    logger.info(f"service request id : {service_request_id}")
    with transaction.atomic():
        if service_request_id not in (None,""):
            current_status = ServiceRequest.objects.filter(id=service_request_id).values_list("status",flat=True).first()
            #   New Service Accepted  ======>> Status 2 ====>> Gig Worker End
            if service_status_to ==2 :
                logger.info(" ===================  NEW SERVICE REQUEST ACCEPTED BY GIG WORKER --- STATUS 2 =============")
                logger.info(f"Current Status : {current_status}")
                if current_status == 1 and service_status_to ==2:
                    code = str(secrets.randbelow(900000)+100000)
                    logger.info(f"code : {code}")
                    serviceRequest_details = ServiceRequest.objects.filter(id=service_request_id).first()
                    if not serviceRequest_details:
                        raise Exception("Service Request Not Found")

                    for field, value in {
                        "status": service_status_to,
                        "booking_code": code,
                        "assigned_to": candidate_id,
                        "assigned_by": citizen_id,
                        "assigned_on": current_datetime,
                        "updated_by": candidate_id,
                        "updated_on": current_datetime
                    }.items():
                        setattr(serviceRequest_details, field, value)

                    serviceRequest_details.save()
                    
                    service_request_lifecycle_object={
                        "service_request": serviceRequest_details,
                        "candidate": candidate_details,
                        "citizen": citizen_details,
                        "service": service_details,
                        "lifecycle_status": service_status_to,
                        "assigned_to": candidate_id,
                        "assigned_by": citizen_id,
                        "remarks": STATUS_2,
                        "created_by": candidate_id,
                        "created_on": current_datetime,
                        "updated_by": None,
                        "updated_on": None,
                    }
                    serviceRequestLifeCycleDetails = ServiceRequestLifecycle.objects.create(**service_request_lifecycle_object)
                    service_request_lifecycle_id=serviceRequestLifeCycleDetails.id
                    logger.info(f"Service Request Accept status Inserted in Lifecycle Table For Service Request Id :: {service_request_id} and Lifecycle Id :: {service_request_lifecycle_id}")
                    logger.info("Service Request Accept status Inserted in Lifecycle Table Successfully")

                    message = "Service Request Accepted By Gig Worker Updated Successfully"
                    logger.info(f"FCM Token :: {citizen_tokens}, Token User Type :: {citizen_user_type}")
                    notificationPayload = {
                        "token": citizen_tokens,
                        "title": "Booking Service Request Status Update",
                        "body": notification.format(name=candidate_name) or STATUS_2_MESSAGE,
                        "data": {
                            "service_request_id": service_request_id,
                            "status":status_name,
                            "navigate_to": "citizen_service_listing"
                        }
                    }
                    sent_status = send_fcm_notification_async(notificationPayload)
                    logger.warning(f"FCM Notification Sent Status :: {sent_status}")
                else:
                    raise Exception("Service Request can't Accepted if it's Already Accepted or not pending")
            #   New Service Rejected  ======>> Status 3 ====>> Gig Worker End
            elif service_status_to ==3 :
                logger.info(" ===================  NEW SERVICE REQUEST REJECTED BY GIG WORKER --- STATUS 3 =============")
                logger.info(f"Current Status : {current_status}")
                if current_status == 1 and service_status_to ==3:
                    ServiceRequest.objects.filter(id=service_request_id).update(
                        service_desc=remarks,
                        status=service_status_to,
                        assigned_to=candidate_id,
                        assigned_by=citizen_id,
                        assigned_on=current_datetime,
                        updated_by=candidate_id,
                        updated_on=current_datetime
                    )
                    service_request_details = ServiceRequest.objects.filter(
                        id=service_request_id
                    ).get()
                    service_request_lifecycle_object = {
                        "service_request": service_request_details,
                        "candidate": candidate_details,
                        "citizen": citizen_details,
                        "service": service_details,
                        "lifecycle_status": service_status_to,
                        "assigned_to": candidate_id,
                        "assigned_by": citizen_id,
                        "remarks": STATUS_3,
                        "created_by": candidate_id,
                        "created_on": current_datetime,
                        "updated_by": None,
                        "updated_on": None, 
                    }
                    serviceRequestLifecycleDetails = ServiceRequestLifecycle.objects.create(**service_request_lifecycle_object)
                    service_request_lifecycle_id=serviceRequestLifecycleDetails.id
                    logger.info(f"Service Request Reject status Inserted in Lifecycle Table For Service Request Id :: {service_request_id} and Lifecycle Id :: {service_request_lifecycle_id}")
                    message="Service Request Rejected By Gig Worker Updated Successfully"
                    logger.info(f"FCM Token :: {citizen_tokens}, Token User Type :: {citizen_user_type}")
                    sent_status=send_fcm_notification_async(
                        token=citizen_tokens,
                        title=title,
                        body=notification.format(name=candidate_name) or STATUS_3_MESSAGE,
                        data={
                            "service_request_id": service_request_id,
                            "status":status_name,
                            "navigate_to": "citizen_service_listing"
                        }
                    )
                    logger.warning(f"FCM Notification Sent Status :: {sent_status} push notification dispatched asynchronous for Citizen User  ID :: {citizen_user_id}")
                else:
                    raise Exception("Service Request can't Rejected if it's Already Accepted or not pending")
                logger.info(" ============ >>> Service Request Rejected  by Gig Worker <<< ============")
                
            #   New Service Cancelled   ======>> Status 5 ====>> Gig Worker End
            elif service_status_to ==5 :
                logger.info(" ================= NEW SERVICE REQUEST CANCELLED BY CITIZEN -----------------")
                logger.info(f"Current Status : {current_status} | Service Status To :: {service_status_to}")
                if current_status == 1 and service_status_to ==5:
                    ServiceRequest.objects.filter(id=service_request_id).update(
                        service_desc=remarks,
                        status=service_status_to,
                        assigned_to=citizen_id,
                        assigned_by=citizen_id,
                        assigned_on=current_datetime,
                        updated_by=citizen_id,
                        updated_on=current_datetime
                    )
                    serviceRequestDetails = ServiceRequest.objects.filter(id=service_request_id).first()
                    service_request_lifecycle_object={
                        "service_request": serviceRequestDetails,
                        "candidate": candidate_details,
                        "citizen": citizen_details,
                        "service": service_details,
                        "lifecycle_status": service_status_to,
                        "assigned_to": citizen_id,
                        "assigned_by": citizen_id,
                        "remarks": STATUS_5,
                        "created_by": citizen_id,
                        "created_on": current_datetime,
                        "updated_by": None,
                        "updated_on": None
                    }
                    serviceRequestCycleDetails=ServiceRequestLifecycle.objects.create(**service_request_lifecycle_object)
                    service_request_lifecycle_id=serviceRequestCycleDetails.id
                    logger.info(f"Service Request Cancelled status Inserted in Lifecycle Table For Service Request Id :: {service_request_id} and Lifecycle Id :: {service_request_lifecycle_id}")
                    message="Service Request Cancelled By Citizen Updated Successfully"
                    logger.info(f"FCM Token :: {citizen_tokens}, Token User Type :: {citizen_user_type}")
                    sent_status=send_fcm_notification_async(
                        token=citizen_tokens,
                        title=title,
                        body=notification.format(name=candidate_name) or STATUS_5_MESSAGE,
                        data={
                            "service_request_id": service_request_id,
                            "status":status_name,
                            "navigate_to": "citizen_service_listing"
                        }
                    )
                    logger.warning(f"FCM Notification Sent Status :: {sent_status} push notification dispatched asynchronous for Citizen User  ID :: {citizen_user_id}")
                else:
                    raise Exception("Service Request can't Cancelled if it's Already Accepted or not pending")
                logger.info(" ============ >>> Service Request Cancelled  by Citizen <<< ============")
            #   New Service Not Completed   ======>> Status 4 ====>> Gig Worker End
            elif service_status_to ==4:
                logger.info(" ================= NEW SERVICE REQUEST completed by citizen - status 4 -----------------")
                logger.info(f"Current Status : {current_status} | Service Status To :: {service_status_to}")
                if current_status == 7 and service_status_to ==4:
                    ServiceRequest.objects.filter(id=service_request_id).update(
                        service_desc=remarks,
                        status=service_status_to,
                        assigned_to=candidate_id,
                        assigned_by=citizen_id,
                        assigned_on=current_datetime,
                        updated_by=citizen_id,
                        updated_on=current_datetime
                    )
                    serviceRequestDetails = ServiceRequest.objects.filter(id=service_request_id).first()
                    service_request_lifecycle_object={
                        "service_request": serviceRequestDetails,
                        "candidate": candidate_details,
                        "citizen": citizen_details,
                        "service": service_details,
                        "lifecycle_status": service_status_to,
                        "assigned_to": candidate_id,
                        "assigned_by": citizen_id,
                        "remarks": STATUS_4,
                        "created_by": citizen_id,
                        "created_on": current_datetime,
                        "updated_by": None,
                        "updated_on": None
                    }
                    serviceRequestLifeCycleDetails = ServiceRequestLifecycle.objects.create(**service_request_lifecycle_object)
                    service_request_lifecycle_id=serviceRequestLifeCycleDetails.id
                    logger.info(f"Service Request Completed status Inserted in Lifecycle Table For Service Request Id :: {service_request_id} and Lifecycle Id :: {service_request_lifecycle_id}")
                    message="Service Request Completed By Citizen Updated Successfully"
                    logger.info(f"FCM Token :: {citizen_tokens}, Token User Type :: {citizen_user_type}")
                    sent_status=send_fcm_notification_async(
                        token=citizen_tokens,
                        title=title,
                        body=notification.format(name=candidate_name) or STATUS_4_MESSAGE,
                        data={
                            "service_request_id": service_request_id,
                            "status":status_name,
                            "navigate_to": "citizen_service_listing"
                        }
                    )
                    logger.warning(f"FCM Notification Sent Status :: {sent_status} push notification dispatched asynchronous for Citizen User  ID :: {citizen_user_id}")
                else:
                    raise Exception("Service Request can't Completed if it's Already Accepted or not pending")  
                logger.info(" ============ >>> Service Request Completed  by Citizen <<< ============")
                
            elif service_status_to ==6:
                logger.info(" ================= NEW SERVICE REQUEST not completed approved by gig worker - status 6 -----------------")
                logger.info(f"Current Status : {current_status} | Service Status To :: {service_status_to}")
                if current_status == 7 and service_status_to ==6:
                    ServiceRequest.objects.filter(id=service_request_id).update(
                        service_desc=remarks,
                        status=service_status_to,
                        assigned_to=candidate_id,
                        assigned_by=citizen_id,
                        assigned_on=current_datetime,
                        updated_by=citizen_id,
                        updated_on=current_datetime
                    )
                    serviceRequestDetails = ServiceRequest.objects.filter(id=service_request_id).first()
                    service_request_lifecycle_object={
                        "service_request": serviceRequestDetails,
                        "candidate": candidate_details,
                        "citizen": citizen_details,
                        "service": service_details,
                        "lifecycle_status": service_status_to,
                        "assigned_to": candidate_id,
                        "assigned_by": citizen_id,
                        "remarks": STATUS_6,
                        "created_by": citizen_id,
                        "created_on": current_datetime,
                        "updated_by": None,
                        "updated_on": None
                    }
                    serviceRequestLifeCycleDetails = ServiceRequestLifecycle.objects.create(**service_request_lifecycle_object)
                    service_request_lifecycle_id=serviceRequestLifeCycleDetails.id
                    logger.info(f"Service Request Not Completed status Inserted in Lifecycle Table For Service Request Id :: {service_request_id} and Lifecycle Id :: {service_request_lifecycle_id}")
                    message="Service Request Not Completed Approved By Citizen Updated Successfully"
                    logger.info(f"FCM Token :: {citizen_tokens}, Token User Type :: {citizen_user_type}")
                    sent_status=send_fcm_notification_async(
                        token=citizen_tokens,
                        title=title,
                        body=notification.format(name=candidate_name) or STATUS_6_MESSAGE,
                        data={
                            "service_request_id": service_request_id,
                            "status":status_name,
                            "navigate_to": "citizen_service_listing"
                        }
                    )
                    logger.warning(f"FCM Notification Sent Status :: {sent_status} push notification dispatched asynchronous for Citizen User  ID :: {citizen_user_id}")
                else:
                    raise Exception("Service Request can't Not Completed if it's Already Accepted or not pending")  
                logger.info(" ============ >>> Service Request Not Completed  by Citizen <<< ============") 
            
            # ! Service Proviced ==== >>> status 7 ====>> Gig Worker End 
            elif service_status_to ==7:
                logger.info(" ================= NEW SERVICE REQUEST provided by gig worker - status 7 -----------------")
                logger.info(f"Current Status : {current_status} | Service Status To :: {service_status_to}")
                if current_status == 1 and service_status_to ==7:
                    
                    #  Booking Code Confirmation 
                    if code not in (None,""):
                        saved_code = ServiceRequest.objects.filter(id=service_request_id).values_list("booking_code",flat=True)
                        if saved_code != code:
                            raise Exception("Invalid Booking Code ... please Try Again sometime later !!")
                        service_request_lifecycle_object={
                            "service_request": serviceRequestDetails,
                            "candidate": candidate_details,
                            "citizen": citizen_details,
                            "service": service_details,
                            "lifecycle_status": service_status_to,
                            "assigned_to": candidate_id,
                            "assigned_by": citizen_id,
                            "remarks": STATUS_7,
                            "created_by": citizen_id,
                            "created_on": current_datetime,
                            "updated_by": None,
                            "updated_on": None
                        }
                        serviceRequestLifeCycleDetails= ServiceRequestLifecycle.objects.create(**service_request_lifecycle_object)
                        service_request_lifecycle_object_id = serviceRequestLifeCycleDetails.id
                        logger.info(f"Service Provided status Inserted in Lifecycle Table For Service Request Id :{service_request_id} and Lifecycle Id :: {service_request_lifecycle_object_id}")
                        logger.info(f"Service Provided status Inserted in Lifecycle Table Successfully")
                        message="Service Request Provided By Gig Worker Updated Successfully"
                        
                        #! Push Notification Return For Status Update 
                        
                        logger.info(f"FCM Token :: {citizen_tokens}, Token User Type :: {citizen_user_type}, Token User ID :: {citizen_user_id}")
                        sent_status = send_fcm_notification_async(token=citizen_tokens,
                                                                  title=title,body=notification.format(name=candidate_name) or STATUS_7_MESSAGE,
                                                                  data={
                                                                      "service_request_id": service_request_id,
                                                                      "status":status_name,
                                                                      "navigate_to": "citizen_service_listing"
                                                                    }
                                                                  )
                        logger.warning(f"Push Notification Status :: {sent_status} Push Notification Dispatched Asynchronously for Citizen User ID :: {citizen_user_id}")1
                    else:
                        raise Exception("Booking Code Not Found, Gig Worker Should Provide Booking Code for Confirmation")
                else:
                    raise Exception("Service Provided can't be Updated if it's not not Already Accepted by Gig Worker")
                logger.info(" ============ >>> Service Provided  by Gig Worker <<< ============")
                
            # ! Service Not Provided =======>>>> status 8 ====>> Citizen End 
            elif service_status_to ==8:
                logger.info(" ================= Service Not Provided Yet Approved by Citizen - status 8 -----------------")
                logger.info(f"Current Status : {current_status} | Service Status To :: {service_status_to}")
                if current_status == 2 and service_status_to == 8:
                    ServiceRequest.objects.filter(id=service_request_id).update(
                        service_desc=remarks,
                        status=service_status_to,
                        assigned_to=candidate_id,
                        assigned_by=citizen_id,
                        assigned_on=current_datetime,
                        updated_by=citizen_id,
                        updated_on=current_datetime
                    )
                    serviceRequestDetails = ServiceRequest.objects.filter(
                        id=service_request_id
                    ).first()
                    service_request_lifecycle_object={
                        "service_request": serviceRequestDetails,
                        "candidate": candidate_details,
                        "citizen": citizen_details,
                        "service": service_details,
                        "lifecycle_status": service_status_to,
                        "assigned_on": current_datetime,
                        "assigned_to": candidate_id,
                        "assigned_by": citizen_id,
                        "remarks": STATUS_8,
                        "created_by": candidate_id,
                        "created_on": current_datetime,
                        "updated_by": None,
                        "updated_on": None,
                        "service_desc": remarks
                    }
                    serviceRequestLifeCycleDetails = ServiceRequestLifecycle.objects.create(**service_request_lifecycle_object)
                    service_request_lifecycle_id = serviceRequestLifeCycleDetails.id
                    logger.info(f"Service Not Provided status Inserted in Lifecycle Table For Service Request Id :: {service_request_id} and Lifecycle Id :: {service_request_lifecycle_id}")
                    logger.info(f"Service Not Provided status Inserted in Lifecycle Table Successfully")
                    message="Service Not Provided Yet Approved By Citizen Updated Successfully"
                    #! Push notification Return For Status Update
                    logger.info("FCM Token :: {citizen_tokens}, Token User Type :: {citizen_user_type}, Token User ID :: {citizen_user_id}")
                    sent_status = send_fcm_notification_async(
                        token=citizen_tokens,
                        title=title,
                        body=notification.format(name=candidate_name) or STATUS_8_MESSAGE,
                        data={
                            "service_request_id": service_request_id,
                            "status":status_name,
                            "navigate_to": "gig_worker_service_listing"
                        }
                    )
                    logger.warning(f"Push Notification Status :: {sent_status} Push Notification Dispatched Asynchronously for Candidate User ID :: {candidate_user_id}")
                else:
                    raise Exception("Service Not Provided can't be Updated if it's not not Already Accepted by Gig Worker")
                logger.info(" ============ >>> Service Not Provided Yet Approved  by Citizen <<< ============")
            
            # ! Service Not Provided =======>>>> status 9 ====>> Gig Worker End
            elif service_status_to ==9:
                logger.info(" ================= Service Decline by Gig Worker - status 9 -----------------")
                logger.info(f"Current Status : {current_status} | Service Status To :: {service_status_to}")
                if current_status == 2 and service_status_to == 9:
                    ServiceRequest.objects.filter(id=service_request_id).update(
                        service_desc=remarks,
                        status=service_status_to,
                        booking_code="DECLINED",
                        assigned_to=candidate_id,
                        assigned_by=citizen_id,
                        assigned_on=current_datetime,
                        updated_by=citizen_id,
                        updated_on=current_datetime
                    )
                    serviceRequestDetails = ServiceRequest.objects.filter(id=service_request_id).first()
                    service_request_lifecycle_object={
                        "service_request": serviceRequestDetails,
                        "candidate": candidate_details,
                        "citizen": citizen_details,
                        "service": service_details,
                        "lifecycle_status": service_status_to,
                        "assigned_to": candidate_id,
                        "assigned_by": citizen_id,
                        "remarks": STATUS_9,
                        "created_by": candidate_id,
                        "created_on": current_datetime,
                        "updated_by": None, 
                        "updated_on": None,
                        "service_desc": remarks
                    }
                    serviceRequestDetails = ServiceRequestLifecycle.objects.create(**service_request_lifecycle_object)
                    service_request_lifecycle_id = serviceRequestDetails.id
                    logger.info(f"Service Decline status Inserted in Lifecycle Table For Service Request Id :: {service_request_id} and Lifecycle Id :: {service_request_lifecycle_id}")
                    logger.info(f"Service Decline status Inserted in Lifecycle Table Successfully")
                    
                    # Decline Question 
                    if question_id not in (None,""):
                        for item in question_id:
                            question_obj = DeclineQuestionMaster.objects.filter(
                                id=item
                            )
                            decline_question_object = {
                                "service_request": serviceRequestDetails,
                                "question": question_obj,
                                "created_by": citizen_id,
                                "created_on": current_datetime,
                                "updated_by": None,
                                "updated_on": None,
                                "remarks": remarks,
                                "is_active": True,
                                "status":ACTIVE,
                                "created_by": citizen_id,
                                "citizen": citizen_details,
                                "candidate": candidate_details,
                                "decline_question": question_obj,
                            }
                            declineQuestionDetails = DeclineQuestionMaster.objects.create(**decline_question_object)
                            decline_question_id = declineQuestionDetails.id
                            logger.info(f"Decline Question Inserted successfully for service request id :: {service_request_id} and Question Id :: {decline_question_id} ")
                            logger.info(f"Decline Question Inserted Successfully")
                    
                    message="Service Decline By Gig Worker Updated Successfully"
                    
                    #! Push Notification Return For Status Update 
                    
                    logger.info(f"FCM Token :: {citizen_tokens}, Token User Type :: {citizen_user_type}, Token User ID :: {citizen_user_id}")
                    sent_status = send_fcm_notification_async(token=citizen_tokens,
                                                              title=title,
                                                              body=notification.format(name=candidate_name) or STATUS_9_MESSAGE,
                                                              data={
                                                                  "service_request_id": service_request_id,
                                                                  "status":status_name,
                                                                  "navigate_to": "citizen_service_listing"
                                                                }
                                                              )
                    logger.warning(f"Push Notification Status :: {sent_status} Push Notification Dispatched Asynchronously for Citizen User ID :: {citizen_user_id}")
                else:
                    raise Exception("Service Decline can't be Updated if it's not not Already Accepted by Gig Worker")
                logger.info(" ============ >>> Service Decline  by Gig Worker ---- Status 9 <<< ============")
            else:
                raise Exception("Service Status Should Not be blank ... Please Choose Correct Service Status for Service Request Update")
            
            # New Service Requested  =============== ???? 
        else:
            
            # ! New Service Requested =====>>>> Status 1 ====>> Citizen End
            if service_status_to ==1:
                logger.info(" ================= NEW SERVICE REQUESTED BY CITIZEN - status 1 -----------------")
                logger.info(f"Current Status : {current_status} | Service Status To :: {service_status_to}")
                # Get Auto Generated Service Code ====>>> 
                # Service Code = "SERE"
                service_code = f"SERE{INT((time.time()))}"
                logger.info(f"Service Code Generated :: {service_code}")
                if preferred_day not in (None,""):
                    if not validate_dob(dob=preferred_day):
                        raise InvalidUsernameFormatException("Invalid Given Date Format. Required Format - YYYY-MM-DD")
                    day_name=get_day_name(preferred_day)
                
                    
                    
                     
                
            
                    
                    
                    

                
                  
                    
                                    
            
            
            
            
    
    
    
    
    
    
    
    
    
    
    

    
    
    