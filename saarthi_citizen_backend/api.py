from django.urls import path
from health.views import (HealthCheck)

urls=[
    path('health/',HealthCheck),
]