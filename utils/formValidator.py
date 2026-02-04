from django import forms
import re
from django.utils import timezone
from datetime import timedelta,datetime


class loginForm(forms.Form):
    username = forms.CharField(max_length=100,required=True)
    password = forms.CharField(max_length=100,required=True)

class OTPGenerateForm(forms.Form):
    username = forms.CharField(max_length=100,required=True)
    

class OTPVerifyForm(forms.Form):
    otp = forms.CharField(max_length=100,required=True)
    username = forms.CharField(max_length=100,required=True)

class OTPResetForm(forms.Form):
    otp = forms.CharField(max_length=100,required=True)
    username = forms.CharField(max_length=100,required=True)

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100,required=True)
    fcm_token = forms.CharField(max_length=100,required=True)
    otp = forms.CharField(max_length=8,required=True)
    
    