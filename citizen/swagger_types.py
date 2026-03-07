from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

otp_success_response = openapi.Response(
    description="OTP sent successfully",
    examples={
        "application/json": {
            "message": "OTP Sent"
        }
    }
)

otp_error_response = openapi.Response(
    description="Error response",
    examples={
        "application/json": {
            "error": "Invalid mobile no or email"
        }
    }
)



otp_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["username"],
    properties={
        "username": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Mobile number or Email ID",
            example="9876543210"
        )
    }
)


citizen_login_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["username", "otp"],
    properties={
        "username": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Mobile number or email"
        ),
        "otp": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="OTP received by user"
        ),
        "fcm_token": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="FCM token (optional)",
            nullable=True
        ),
    }
)


citizen_login_success_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "Code": openapi.Schema(type=openapi.TYPE_INTEGER),
        "Message": openapi.Schema(type=openapi.TYPE_STRING),
        "citizen_data": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description="Citizen profile data",
            additional_properties=True
        )
    }
)

citizen_login_error_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "error": openapi.Schema(type=openapi.TYPE_STRING)
    }
)


citizen_register_success_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "Code": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            example=200
        ),
        "Message": openapi.Schema(
            type=openapi.TYPE_STRING,
            example="Citizen Registered Successfully"
        ),
        "auth_token": openapi.Schema(
            type=openapi.TYPE_STRING,
            example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        ),
        "registered_data": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "citizen_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    example=123
                ),
                "user_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    example=456
                ),
            }
        )
    }
)

citizen_register_error_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "Code": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            example=400
        ),
        "Message": openapi.Schema(
            type=openapi.TYPE_STRING,
            example="Invalid mobile no"
        )
    }
)



citizen_register_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=[
        "first_name",
        "last_name",
        "gender",
        "dob",
        "mobile_no",
        "email",
        "state_id",
        "district_id",
        "pincode"
    ],
    properties={
        "user_id": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description="Existing user ID (required for profile update)"
        ),
        "citizen_id": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description="Existing citizen ID (required for profile update)"
        ),
        "first_name": openapi.Schema(
            type=openapi.TYPE_STRING,
            example="Manoj"
        ),
        "middle_name": openapi.Schema(
            type=openapi.TYPE_STRING,
            example="Kumar"
        ),
        "last_name": openapi.Schema(
            type=openapi.TYPE_STRING,
            example="Santra"
        ),
        "gender": openapi.Schema(
            type=openapi.TYPE_STRING,
            example="M"
        ),
        "dob": openapi.Schema(
            type=openapi.TYPE_STRING,
            format="date",
            example="1998-05-21"
        ),
        "mobile_no": openapi.Schema(
            type=openapi.TYPE_STRING,
            example="9876543210"
        ),
        "email": openapi.Schema(
            type=openapi.TYPE_STRING,
            format="email",
            example="manoj@example.com"
        ),
        "state_id": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            example=10
        ),
        "district_id": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            example=101
        ),
        "block_id": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            example=1001,
            description="Optional block ID"
        ),
        "pincode": openapi.Schema(
            type=openapi.TYPE_STRING,
            example="721101"
        ),
    }
)
