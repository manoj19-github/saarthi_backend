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
class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=100, required=True)
    middle_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=True)

    gender = forms.ChoiceField(
        choices=[
            ("M", "Male"),
            ("F", "Female"),
            ("O", "Other"),
        ],
        required=True
    )

    dob = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={"type": "date"})
    )

    mobile_no = forms.CharField(max_length=15, required=True)
    email = forms.EmailField(required=True)

    state_id = forms.IntegerField(required=True)
    district_id = forms.IntegerField(required=True)
    block_id = forms.IntegerField(required=False)

    pincode = forms.CharField(max_length=6, required=True)




class CitizenServiceRequestForm(forms.Form):
    service_request_id = forms.IntegerField(required=False)
    citizen_id = forms.IntegerField(required=True)
    candidate_id = forms.IntegerField(required=True)
    service_id = forms.IntegerField(required=True)
    district_id = forms.IntegerField(required=True)
    service_status_to = forms.IntegerField(required=True)

    remarks = forms.CharField(max_length=500, required=False)
    preferred_day = forms.DateField(required=False)

    address_id = forms.IntegerField(required=False)

    start_time = forms.TimeField(required=False)
    end_time = forms.TimeField(required=False)

    code = forms.CharField(max_length=50, required=False)
    question_id = forms.IntegerField(required=False)

    # 🔥 Cross-field validation
    def clean(self):
        cleaned_data = super().clean()

        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError("Start time must be before end time.")

        return cleaned_data