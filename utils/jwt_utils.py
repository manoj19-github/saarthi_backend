import jwt 
from django.conf import settings
from datetime import datetime, timedelta


def generate_jwt_token(payload):
    """
    Generate a JWT token with the given payload.
    The token will expire in 1 hour.
    """
    expiration = datetime.utcnow() + settings.JWT_EXPIRATION_TIME
    payload["exp"] = expiration
    payload["environment"] = settings.ENVIRONMENT
    
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_jwt(token):
    try:
        
        return jwt.decode(token,settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
    except Exception as e:
        raise ValueError(e)

