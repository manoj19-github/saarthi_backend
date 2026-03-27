from django.db import models
from common.models import (User, State, District, Block, Sector, Skill, Services, DocumentMaster)
from gigworkers.models import (Candidate)


class Citizen(models.Model):
    id = models.AutoField(primary_key=True)
    user_type = models.IntegerField(null=True, blank=False)
    first_name = models.CharField(max_length=50,blank=False,null=True)
    middle_name = models.CharField(max_length=50,blank=False,null=True)
    last_name = models.CharField(max_length=50,blank=False,null=True)
    gender = models.CharField(max_length=50,blank=False,null=True)
    date_of_birth = models.DateField(blank=False,null=True)
    mobile_number = models.CharField(max_length=15,blank=False,null=True)
    alter_number = models.CharField(max_length=15,blank=False,null=True)
    email = models.CharField(max_length=100,blank=False,null=True)
    pincode = models.CharField(max_length=6,blank=False,null=True)
    status = models.SmallIntegerField(default=1,blank=False,null=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='citizen_state', blank=True,null=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='citizen_distirct', blank=True,null=True)
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='citizen_block', blank=True,null=True)
    created_by = models.IntegerField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True,blank=False,null=True)
    

    class Meta:
        managed = True
        db_table = "citizen"


class CitizenAddress(models.Model):
    id = models.AutoField(primary_key=True)
    address_line_1 = models.CharField(max_length=100,blank=False,null=True)
    address_line_2 = models.CharField(max_length=100,blank=False,null=True)
    land_mark = models.CharField(max_length=50,blank=False,null=True)
    city = models.CharField(max_length=50,blank=False,null=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='citizen_district', blank=True,null=True)
    state = models.CharField(max_length=50,blank=False,null=True)
    country = models.CharField(max_length=50,blank=False,null=True)
    pincode = models.CharField(max_length=50,blank=False,null=True)
    lattitude = models.CharField(max_length=50,blank=False,null=True)
    longitude = models.CharField(max_length=50,blank=False,null=True)
    is_primary = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=1,blank=False,null=True)
    created_by = models.IntegerField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True,blank=False,null=True)
    citizen = models.ForeignKey(Citizen, on_delete=models.CASCADE, related_name='citizen_address_fk_1')

    class Meta:
        managed = True
        db_table = "citizen_address"


class LoginActivity(models.Model):
    id =  models.BigAutoField(primary_key=True)
    m_no = models.CharField(max_length=50,blank=False,null=True)
    user_type = models.IntegerField(blank=False,null=True)
    login_time = models.DateTimeField(blank=False,null=True)
    logout_time = models.DateTimeField(blank=False,null=True)
    active_status = models.SmallIntegerField(default=1,blank=False,null=True)
    created_on = models.DateTimeField(blank=False,null=True)
    updated_on = models.DateTimeField(blank=False,null=True)

    class Meta:
        managed = True
        db_table = 'login_activity'


class ServiceRequest(models.Model):
    id = models.BigAutoField(primary_key=True)
    service_code = models.CharField(max_length=50,blank=False,null=True)
    citizen =  models.ForeignKey(Citizen, on_delete=models.CASCADE, null=True, blank=True)
    candidate =  models.ForeignKey(Candidate, on_delete=models.CASCADE, null=True, blank=True)
    sector =  models.ForeignKey(Sector, on_delete=models.CASCADE, null=False, blank=True)
    skill =  models.ForeignKey(Skill, on_delete=models.CASCADE, null=False, blank=True)
    service =  models.ForeignKey(Services, on_delete=models.CASCADE, null=False, blank=True)
    district =  models.ForeignKey(District, on_delete=models.CASCADE, null=False, blank=True)
    block =  models.ForeignKey(Block, on_delete=models.CASCADE, null=True, blank=True)
    status = models.SmallIntegerField(blank=False,null=True)
    is_active = models.BooleanField(default=True)
    service_desc = models.CharField(max_length=1000,blank=False,null=True)
    preferred_day = models.SmallIntegerField(blank=False,null=True)
    preferred_date = models.DateField(blank=False,null=True)
    start_time = models.TimeField(blank=False,null=True)
    end_time = models.TimeField(blank=False,null=True)
    address = models.ForeignKey(CitizenAddress, on_delete=models.CASCADE, null=True, blank=True)
    booking_code = models.CharField(max_length=10,blank=True,null=True)
    assigned_to = models.BigIntegerField(blank=False,null=True)
    assigned_by = models.BigIntegerField(blank=False,null=True)
    assigned_on = models.DateTimeField(blank=False,null=True)
    created_by = models.BigIntegerField(blank=False,null=True)
    created_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)
    updated_by = models.BigIntegerField(blank=False,null=True)
    updated_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)

    class Meta:
        managed = True
        db_table = 'service_request'


class ServiceRequestGigworker(models.Model):
    id = models.BigAutoField(primary_key=True)
    service_request =  models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, null=False, blank=True)
    candidate =  models.ForeignKey(Candidate, on_delete=models.CASCADE, null=False, blank=True)
    responce_status = models.SmallIntegerField(default=1,blank=False,null=True)
    created_by = models.BigIntegerField(blank=False,null=True)
    created_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)
    updated_by = models.BigIntegerField(blank=False,null=True)
    updated_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)

    class Meta:
        managed = True
        db_table = 'service_request_gigworker'     


class ServiceReview(models.Model):
    id = models.BigAutoField(primary_key=True)
    request =  models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, null=False, blank=True)
    citizen =  models.ForeignKey(Citizen, on_delete=models.CASCADE, null=False, blank=True)
    candidate =  models.ForeignKey(Candidate, on_delete=models.CASCADE, null=False, blank=True)
    ratings = models.SmallIntegerField(default=1,blank=False,null=True)
    remarks = models.CharField(max_length=500,blank=False,null=True)
    created_by = models.BigIntegerField(blank=False,null=True)
    created_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)
    updated_by = models.BigIntegerField(blank=False,null=True)
    updated_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)

    class Meta:
        managed = True
        db_table = 'service_review' 


class ServiceSearchLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    citizen =  models.ForeignKey(Citizen, on_delete=models.CASCADE, null=False, blank=True)
    search_text = models.CharField(max_length=500,blank=False,null=True) 
    search_date = models.DateTimeField(auto_now_add=True,blank=False,null=True)
    created_by = models.BigIntegerField(blank=False,null=True)
    created_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)
    updated_by = models.BigIntegerField(blank=False,null=True)
    updated_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)

    class Meta:
        managed = True
        db_table = 'service_search_log'  


class AppBanner(models.Model):
    id = models.BigAutoField(primary_key=True)
    app_type = models.CharField(max_length=50,blank=False,null=True) 
    banner_type = models.SmallIntegerField(default=1,blank=False,null=True)
    page = models.CharField(max_length=50,blank=False,null=True) 
    position = models.CharField(max_length=50,blank=False,null=True) 
    is_active = models.BooleanField(default=True)
    priority = models.BooleanField(default=True)
    title = models.CharField(max_length=500,blank=False,null=True) 
    sub_title = models.CharField(max_length=500,blank=False,null=True) 
    document =  models.ForeignKey(DocumentMaster, on_delete=models.CASCADE, null=False, blank=True)
    mime_type =  models.CharField(max_length=50,blank=False,null=True) 
    width_dp = models.BigIntegerField(blank=False,null=True)
    height_dp = models.BigIntegerField(blank=False,null=True)
    background_color = models.CharField(max_length=50,blank=False,null=True) 
    text_color =  models.CharField(max_length=50,blank=False,null=True) 
    theme =  models.CharField(max_length=50,blank=False,null=True)
    border_radius = models.SmallIntegerField(default=1,blank=False,null=True)
    document =  models.ForeignKey(District, on_delete=models.CASCADE, null=False, blank=True)
    start_date = models.DateTimeField(auto_now_add=True,blank=False,null=True)
    end_date = models.DateTimeField(auto_now_add=True,blank=False,null=True)
    created_by = models.BigIntegerField(blank=False,null=True)
    created_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)
    updated_by = models.BigIntegerField(blank=False,null=True)
    updated_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)

    class Meta:
        managed = True
        db_table = 'app_banner'  
        
class ServiceRequestLifecycle(models.Model):
    id = models.BigAutoField(primary_key=True)
    service_request =  models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, null=False, blank=True)
    candidate =  models.ForeignKey(Candidate, on_delete=models.CASCADE, null=False, blank=True)
    citizen =  models.ForeignKey(Citizen, on_delete=models.CASCADE, null=True, blank=True)
    service =  models.ForeignKey(Services, on_delete=models.CASCADE, null=False, blank=True)
    lifecycle_status = models.SmallIntegerField(blank=False,null=True)
    remarks = models.CharField(max_length=255,blank=False,null=True)
    service_desc = models.CharField(max_length=1000,blank=False,null=True)
    assigned_to = models.BigIntegerField(blank=False,null=True)
    assigned_by = models.BigIntegerField(blank=False,null=True)
    assigned_on = models.DateTimeField(blank=False,null=True)
    created_by = models.BigIntegerField(blank=False,null=True)
    created_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)
    updated_by = models.BigIntegerField(blank=False,null=True)
    updated_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)

    class Meta:
        managed = True
        db_table = 'service_request_lifecycle'


class RattingQuestionMaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    ratting_id = models.BigIntegerField(blank=False,null=True)
    question_text = models.CharField(max_length=500,blank=False,null=True)
    is_active = models.BooleanField(default=True)
    status = models.SmallIntegerField(default=1,blank=False,null=True)
    created_by = models.BigIntegerField(blank=False,null=True)
    created_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)
    updated_by = models.BigIntegerField(blank=False,null=True)
    updated_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)
    
    class Meta:
        managed = True
        db_table = 'ratting_question_master'


class ServiceRattingAnswer(models.Model):
    id = models.BigAutoField(primary_key=True)
    service_review =  models.ForeignKey(ServiceReview, on_delete=models.CASCADE, null=False, blank=True)
    ratting_question =  models.ForeignKey(RattingQuestionMaster, on_delete=models.CASCADE, null=False, blank=True)
    remarks = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=1,blank=False,null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.BigIntegerField(blank=False,null=True)
    created_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)
    updated_by = models.BigIntegerField(blank=False,null=True)
    updated_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)

    class Meta:
        managed = True
        db_table = 'service_ratting_answer'
        
        
class DeclineQuestionMaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    question_text = models.CharField(max_length=500,blank=False,null=True)
    is_active = models.BooleanField(default=True)
    status = models.SmallIntegerField(default=1,blank=False,null=True)
    created_by = models.BigIntegerField(blank=False,null=True)
    created_on = models.DateTimeField(blank=False,null=True)
    updated_by = models.BigIntegerField(blank=False,null=True)
    updated_on = models.DateTimeField(blank=False,null=True)

    class Meta:
        managed = True
        db_table = 'decline_question_master'


class DeclineAnswer(models.Model):
    id = models.BigAutoField(primary_key=True)
    decline_question =  models.ForeignKey(DeclineQuestionMaster, on_delete=models.CASCADE, null=False, blank=True)
    service_request =  models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, null=False, blank=True)
    citizen =  models.ForeignKey(Citizen, on_delete=models.CASCADE, null=False, blank=True)
    candidate =  models.ForeignKey(Candidate, on_delete=models.CASCADE, null=False, blank=True)
    remarks = models.CharField(max_length=500,blank=False,null=True)
    status = models.SmallIntegerField(default=1,blank=False,null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.BigIntegerField(blank=False,null=True)
    created_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)
    updated_by = models.BigIntegerField(blank=False,null=True)
    updated_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)

    class Meta:
        managed = True    
        db_table = 'decline_answer'


class CitizenAddress(models.Model):
    id = models.AutoField(primary_key=True)
    address_line_1 = models.CharField(max_length=100,blank=False,null=True)
    address_line_2 = models.CharField(max_length=100,blank=False,null=True)
    land_mark = models.CharField(max_length=50,blank=False,null=True)
    city = models.CharField(max_length=50,blank=False,null=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='citizen_district', blank=True,null=True)
    state = models.CharField(max_length=50,blank=False,null=True)
    country = models.CharField(max_length=50,blank=False,null=True)
    pincode = models.CharField(max_length=50,blank=False,null=True)
    lattitude = models.CharField(max_length=50,blank=False,null=True)
    longitude = models.CharField(max_length=50,blank=False,null=True)
    is_primary = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=1,blank=False,null=True)
    created_by = models.IntegerField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True,blank=False,null=True)
    citizen = models.ForeignKey(Citizen, on_delete=models.CASCADE, related_name='citizen_address_fk_1')
    class Meta:
        managed = True
        db_table = "citizen_address"
        

