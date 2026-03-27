DB_ALIAS_MASTER = "default"
DB_ALIAS_REPLICA = "replica"
FIXED_OTP="111111"

#   Time Format
OPS_STRF_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DB_STRF_TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
OS_STRF_TIME = "%d-%m-%Y %I:%M:%S %p"

PHONE_REGEX = r"^[6789]{1}\d{9}$"
EMAIL_REGEX = r"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"
NAME_REGEX = r"^[a-zA-Z\s'\-]+$"
PIN_REGEX= r"^[0-9]{6,6}$"
DOB_REGEX = r"^\d{4}-\d{2}-\d{2}$"
PINCODE_REGEX = r"^[1-9][0-9]{5}$"
AADHAR_REGEX = r"^[2-9]{1}[0-9]{11}$"

USED = "USED"
EXPIRED = "EXPIRED"
DEFAULT_TIMEDIFF = 10
ACTIVE=1
INACTIVE=0

TITLE = "Booking Service Request Status Update"
STATUS_1 = "New Service Requested"
STATUS_2 = "New Service Accepted By Gig Worker"
STATUS_3 = "New Service Rejected By Gig Worker"
STATUS_4 = "Service Completed Approved By Citizen"
STATUS_5 = "Service Request Cancelled By Citizen"
STATUS_6 = "Service Not Completed Approved By Citizen"
STATUS_7 = "Service Provided By Gig Worker"
STATUS_8 = "Service Not Provided Yet Approved By Citizen"
STATUS_9 = "Service Declined By Gig Worker"



STATUS_1_MESSAGE = "You Get a New Service Request From {name}. Please Take a Look !!"
STATUS_2_MESSAGE = "Your Service Request Accepted By Your Choosen Gig Worker {name}. Please Take a Look!!"
STATUS_3_MESSAGE = "Your Service Request Rejected By Your Choosen Gig Worker {name}. Please Request For a New Service!!"
STATUS_4_MESSAGE = "The Service Request Has Been Successfully Completed By {name}. Thank You For Your Hard Work. Please Review The Updated Status !!"
STATUS_5_MESSAGE = "The Service Requested of You Has Been Cancelled By {name}. Please Take a Look!!"
STATUS_6_MESSAGE = "{name} Has Flagged The Service As 'Incomplete'. Please Contact {name} To Resolve Any Outstanding Tasks !!"        
STATUS_7_MESSAGE = "Good News! Gig Worker {name} Has Successfully Completed Your Service Request. Please Check The Work and Let Us Know What You Think!!"
STATUS_8_MESSAGE = "{name} Has Flagged This Service As 'Service Not Provided' Due To Inactivity. Please Ensure Timely Completion of Accepted Requests To Avoid This in the Future!!"
STATUS_9_MESSAGE = "The Assigned Gig Worker {name} Has Declined This Request. We Apologize For The Inconvenience. Please tap Here To Assign A New Worker Immediately !!"

