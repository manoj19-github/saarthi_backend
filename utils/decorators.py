from functools import wraps
import json
from django.conf import settings
from django.http import HttpResponseNotAllowed, JsonResponse
from django_ratelimit.decorators import ratelimit
from users.models import User
from utils.jwt_utils import decode_jwt


def require_post(func):
    """
    Decorator to ensure that a view only accepts POST requests.
    """
    def wrapper(request, *args, **kwargs):
        if request.method != 'POST':
            
            return HttpResponseNotAllowed(['POST'])
        return func(request, *args, **kwargs)
    return wrapper

def jwt_auth_require(view_func):
    """
    Decorator to ensure that a view requires JWT authentication.
    Assumes the JWT token is passed in the 'Authorization' header.
    """
    def wrapper(request, *args, **kwargs):
        """   Decorator for checking JWT authentication """
        request.is_authenticated = False
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({
                'error': 'Authorization header must be included and start with Bearer'
            })
        token = auth_header.split(' ')[1]
        try:
            payload = decode_jwt(token)
            request.user = User.objects.get(id=payload['user_id'])
            request.is_authenticated = True
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=408)
        except User.DoesNotExist:
            return JsonResponse({
                'error': 'User not found'
            }, status=404)
        data={}
        
        # handle GET parameters
        if request.method=='GET':
            data.update(request.GET.dict())
        # handle POST parameters
        if request.method=='POST':
            data.update(request.POST.dict())
        
        # handle raw json body 
        try:
            body = json.loads(request.body.decode('utf-8'))
            if isinstance(body, dict):
                data.update(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
        request.data = data
        return view_func(request, *args, **kwargs)
    return wrapper

#   For Validate Form 
def validate_form(form_class):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.method != 'POST':
                return JsonResponse({
                    'error': 'Method not allowed'
                }, status=400)
            
            data = getattr(request, 'data', request.POST).copy()
            try:
                if request.is_authenticated and hasattr(request, 'user'):
                    user_data = getattr(request.user,"__dict__",{})
                    if "user_type_id" in user_data:
                       data["user_type_id"] = request.user.get("user_type_id")
                    if "user_id" in user_data:
                        data["user_id"] = request.user.get("user_id")
            except Exception as e:
                pass
                    
            form = form_class(request.data)
            if not form.is_valid():
                return JsonResponse({
                    'error': form.errors
                }, status=400)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


# Get Client IP Address
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

def ratelimit_with_ip_whitelist(rate="20/30m",method="POST",key="ip"):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            client_ip = get_client_ip(request)
            whitelist = getattr(settings, 'RATE_LIMIT_WHITELIST_IPS', [])
            if client_ip in whitelist:
                # skip rate limiting for whitelisted IPs
                return view_func(request, *args, **kwargs)
            decorated_view = ratelimit(rate=rate, method=method, key=key)(view_func)
            return decorated_view(request, *args, **kwargs)
        return _wrapped_view
    return decorator



    
            
    
            
        
    