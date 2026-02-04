# ERROR FRAMEWORK
"""
    Master Error Framework
"""
#! Error Keys

DATA = 'Data'
ERROR = 'Errors'
TOKEN = 'Token'
STATUS_CODE = 'status_code'
EXCEPTION = 'Exception'
CODE = 'Code'
MESSAGE = 'Message'
ALERT = 'Alert'

#! SUCCESS CODES ====
SUCCESS_STATUS = 200

SUCCESSCODE = 'SUCCESS001'
SUCCESSMESSAGE = 'Success'

SUCCESSCODE2 = 'SUCCESS002'
SUCCESSMESSAGE2 = 'OTP Generated Successfully'

SUCCESSCODE3 = 'SUCCESS003'
SUCCESSMESSAGE3 = 'User Logout Successfully'

SUCCESSCODE4 = 'SUCCESS004'
SUCCESSMESSAGE4 = 'User Login Successfully'

SUCCESSCODE5 = 'SUCCESS005'
SUCCESSMESSAGE5 = 'User Login Successfully But Yet not Verified.... !!, Please Register Yourself for Exploring More Features'

SUCCESSCODE6 = 'SUCCESS006'
SUCCESSMESSAGE6 = 'User Registered Successfully'



#! Generic Messages :: ======
SUCCESS_MESSAGES = {
    "SUCCESS001": "Success",
    "SUCCESS002": "OTP Generated Successfully",
    "SUCCESS003": "User Logout Successfully",
    "SUCCESS004": "User Login Successfully",
    "SUCCESS005": "User Login Successfully But Yet not Verified.... !!, Please Register Yourself for Exploring More Features",
    "SUCCESS006": "User Registered Successfully",
    "E00100155":  "PAGE NOT FOUND / LIMIT EXCEEDED"
}

#! Error Codes & Error Messages [System, Information, Business & Warning]
"""
    BUSINESS ERROR
"""
BUSSINESS_EXC_STATUS = 310

BE001 = 'BE001'
BE001MESSAGE = 'Missing Mandatory Inputs.'

BE002 = 'BE002'
BE002MESSAGE = '{} not found'

BE003 = 'BE003'
BE003MESSAGE = '{} found'

BE004 = 'BE004'
BE004MESSAGE = 'Condition Not Satisfied.'

BE005 = 'BE005'
BE005MESSAGE = 'File Upload Failure'

BE006 = 'BE006'
BE006MESSAGE = 'File Download Failure'

BE007 = 'BE007'
BE007MESSAGE = 'Please Select A Different Date Range.'

BE008 = 'BE008'
BE008MESSAGE = 'No Data Available.'

"""
    INFORMATIONAL ERROR
"""
INFO_EXC_STATUS = 311

IN001 = "IN001"
IN001MESSAGE = "Username Must be a Phone Number or an Email"

IN002 = "IN002"
IN002MESSAGE = "Please Provide a Valid Primary Phone Number"

IN003 = "IN003"
IN003MESSAGE = "Please Provide a Valid Email Id"

IN004 = "IN004"
IN004MESSAGE = "OTP has already been sent to your mobile number. Valid for {} minutes If you have not received the OTP, please try again after {}."

IN005 = "IN005"
IN005MESSAGE = "Invalid Mobile Number Format"

"""
    SYSTEM ERRORS
"""
SYS_EXC_STATUS = 312

SE001 = 'SE001'
SE001MESSAGE = 'Oops!!! Something Went Wrong. Please Try Again Later.'

SE002 = 'SE002'
SE002MESSAGE = 'Operational Error'

SE003 = 'SE003'
SE003MESSAGE = 'Database Connection Error'

"""
    WARNINGS
"""
WARN_EXC_STATUS = 313

WA001 = 'WA001'
WA001MESSAGE = 'OTP Expired'

WA002 = 'WA002'
WA002MESSAGE = 'Invalid OTP'

WA003 = 'WA003'
WA003MESSAGE = 'Duplicate {} Entry Found'

WA004 = 'WA004'
WA004MESSAGE = 'No OTP Found. Please Request for a New OTP'

WA005 = 'WA005'
WA005MESSAGE = 'Operation not permitted'

WA006 = 'WA006'
WA006MESSAGE = 'Unauthorized Access'

WA007 = 'WA007'
WA007MESSAGE = 'No Data Available'

WA008 = 'WA008'
WA008MESSAGE = 'User Has Been Logged Out Already.'

WA009 = 'WA009'
WA009MESSAGE = 'Invalid Pincode Format'

WA010 = 'WA010'
WA010MESSAGE = 'Your account is currently inactive. Please contact the administrator.'

WA011 = 'WA011'
WA011MESSAGE = '{} is currently inactive. Please contact the administrator.'

#! CLIENT ERROR -- Status Codes
NO_CONTENT_EXC_STATUS = 204
OPERATIONAL_EXCEPTION = 230
DETAIL_LIST_EXCEED_ERROR = 231
TICKET_NOT_FOUND_EXCEPTION = 232
MADATORY_FIELD_NOT_FOUND_EXCEPTION = 233
GEN_EXCEPTION = 234
BAD_REQUEST = 400
UNAUTHORIZE_ACCESS = 401
FORBIDDEN = 403
USER_NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405
REQUEST_TIMEOUT = 408
UNSUPPORTED_MEDIA = 415
INTERNAL_SERVER_ERROR = 500

SUCCESS_STATUS = 200

SUCCESSCODE = 'SUCCESS001'
SUCCESSMESSAGE = 'Success'

SUCCESSCODE2 = 'SUCCESS002'
SUCCESSMESSAGE2 = 'OTP Generated Successfully'

SUCCESSCODE3 = 'SUCCESS003'
SUCCESSMESSAGE3 = 'User Logout Successfully'

SUCCESSCODE4 = 'SUCCESS004'
SUCCESSMESSAGE4 = 'User Login Successfully'

SUCCESSCODE5 = 'SUCCESS005'
SUCCESSMESSAGE5 = 'User Login Successfully But Yet not Verified.... !!, Please Register Yourself for Exploring More Features'

SUCCESSCODE6 = 'SUCCESS006'
SUCCESSMESSAGE6 = 'User Registered Successfully'

SUCCESSCODE7 = 'SUCCESS007'
SUCCESSMESSAGE7 = 'Citizen Service Request Status Updated Successfully'



#! Generic Messages :: ======
SUCCESS_MESSAGES = {
    "SUCCESS001": "Success",
    "SUCCESS002": "OTP Generated Successfully",
    "SUCCESS003": "User Logout Successfully",
    "SUCCESS004": "User Login Successfully",
    "SUCCESS005": "User Login Successfully But Yet not Verified.... !!, Please Register Yourself for Exploring More Features",
    "SUCCESS006": "User Registered Successfully",
    "SUCCESS007": "Citizen Service Request Status Updated Successfully"
}

#! ==============================================================================================
#! ======================================== EOF =================================================
#! ==============================================================================================