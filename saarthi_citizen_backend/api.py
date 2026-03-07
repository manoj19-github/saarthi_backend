from django.urls import path
from citizen.views import citizenLogin, citizenOTPGenerate, citizenRegister
from health.views import (HealthCheck)

urls=[
    path('health/',HealthCheck),
    path('user/generateotp/', citizenOTPGenerate),
    path("user/login/",citizenLogin),
    path("citizen/register/",citizenRegister),
]