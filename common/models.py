from django.db import models
from gigworkers.models import Candidate

# Create your models here.

#! Error Message Model =======
class ErrorMessage(models.Model):
    code = models.CharField(max_length=50, primary_key=True)
    message = models.TextField()
    level_of_severity = models.IntegerField(default=3)
    status = models.BooleanField(default=True)
    err_cd = models.CharField(max_length=5,null=True,blank=False)
    err_msg = models.CharField(max_length=500,null=True,blank=False)
    status_code = models.SmallIntegerField(default=500,blank=False,null=True)

    class Meta:
        managed = False
        db_table = 'error_message'

    def __str__(self):
        return f"{self.code}: {self.message}"


#! Domain Lookup Model =======
class DomainLookup(models.Model):
    domain_id = models.AutoField(primary_key=True)
    domain_type = models.CharField(max_length=50,db_index=True)
    domain_value = models.CharField(max_length=500)
    domain_code = models.IntegerField(null=True,blank=True)
    domain_desc = models.TextField(null=True,blank=True)
    domain_data_type = models.CharField(max_length=50,null=True,blank=True)
    status = models.SmallIntegerField(default=1)

    class Meta:
        managed = False
        db_table = "domain_lookup"


#! Parameter Data Models 
class ParameterMaster(models.Model):
    param_id = models.BigAutoField(primary_key=True)
    parameter_key = models.CharField(max_length=100,blank=False,null=True)
    parameter_value = models.CharField(max_length=600,blank=False,null=False)
    parameter_desc = models.CharField(max_length=255,blank=False,null=True)
    status = models.SmallIntegerField(default=1,blank=False,null=False)
    
    class Meta:
        managed = False
        db_table = "parameter_master"


class EmailFailureTracking(models.Model):
    track_id = models.BigAutoField(primary_key=True)
    recipient = models.CharField(max_length=255,blank=False,null=True)
    subject = models.CharField(max_length=255,blank=False,null=True)
    content = models.TextField(blank=False,null=True)
    sent_status = models.SmallIntegerField(blank=False,null=True)
    mail_sent_on = models.DateTimeField(blank=False,null=True)
    exception = models.CharField(max_length=100,blank=False,null=True)
    created_on = models.DateTimeField(blank=False,null=True)
    updated_on = models.DateTimeField(blank=False,null=True)

    class Meta:
        managed = True
        db_table = "email_failure_tracking"


class SmsFailureTracking(models.Model):
    track_id = models.BigAutoField(primary_key=True)
    recipient = models.CharField(max_length=255,blank=False,null=True)
    sms_header = models.CharField(max_length=8,blank=False,null=True)
    template_id = models.CharField(max_length=255,blank=False,null=True)
    content = models.TextField(blank=False,null=True)
    sent_status = models.SmallIntegerField(blank=False,null=True)
    sms_sent_on = models.DateTimeField(blank=False,null=True)
    exception = models.CharField(max_length=100,blank=False,null=True)
    created_on = models.DateTimeField(blank=False,null=True)
    updated_on = models.DateTimeField(blank=False,null=True)

    class Meta:
        managed = True
        db_table = "sms_failure_tracking"


class AuditLog(models.Model):
    audit_id = models.BigAutoField(primary_key=True)
    table_name = models.CharField(blank=False,null=True)
    operation = models.CharField(blank=False,null=True)
    ref_id = models.IntegerField(blank=False,null=True) 
    old_candidate_data = models.JSONField(blank=False,null=True)
    old_training_data = models.JSONField(blank=False,null=True)
    updated_by = models.BigIntegerField(blank=False,null=True)
    updated_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)
    remarks = models.CharField(blank=False,null=True)

    class Meta:
        managed = False
        db_table = 'audit_log'


#! User Model =======
class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    user_type = models.IntegerField(null=True, blank=False)
    ref_id = models.IntegerField(blank=True, null=True)
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True)
    login_flag = models.BooleanField(default=False,blank=False,null=True)
    status = models.SmallIntegerField(default=1,blank=False,null=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(blank=False,null=False)
    updated_on = models.DateTimeField(blank=False,null=False)
    created_by = models.IntegerField(blank=True, null=True)
    updated_by = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "user"

    def __str__(self):
        return f"{self.username}"


#! User OTP Model =======
class UserOtp(models.Model):
    TYPE_CHOICES = [
        (1, 'PHONE'),
        (2, 'EMAIL'),
        (3, 'ALL'),
    ]
    otp_id = models.BigAutoField(primary_key=True)
    u_phone = models.CharField(max_length=15, blank=True, null=True)
    u_email = models.CharField(max_length=100, blank=True, null=True)
    otp = models.CharField(max_length=8,blank=False,null=True)
    created_on = models.DateTimeField(blank=False,null=True)
    updated_on = models.DateTimeField(blank=False,null=True)
    expiry_time = models.DateTimeField(blank=False,null=True)
    otp_lock_time = models.DateTimeField(blank=False,null=True)
    otptype = models.SmallIntegerField(choices=TYPE_CHOICES)
    
    class Meta:
        managed = True
        db_table = "user_otp"


class State(models.Model):
    id = models.AutoField(primary_key=True)
    state_name = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    updated_by = models.IntegerField(null=True, blank=True)
    status = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'state_master'

    def __str__(self):
        return self.state_name


class District(models.Model):
    id = models.AutoField(primary_key=True)
    district_name = models.CharField(max_length=50)
    district_code = models.CharField(max_length=50)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, related_name='districts')
    is_active = models.BooleanField(default=True)
    is_required = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    updated_by = models.IntegerField(null=True, blank=True)
    status = models.SmallIntegerField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'district_master'
    
    def __str__(self):
        return self.district_name


class Block(models.Model):
    id = models.AutoField(primary_key=True)
    block_name = models.CharField(max_length=50)
    block_code = models.CharField(max_length=50)
    district = models.ForeignKey(District, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    updated_by = models.IntegerField(null=True, blank=True)
    status = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'block_master'

    def __str__(self):
        return f"{self.block_name} ({self.district.district_name})"
    

class Sector(models.Model):
    id = models.AutoField(primary_key=True)
    sector_name = models.CharField(max_length=50)
    sector_type = models.SmallIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_required = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    updated_by = models.IntegerField(null=True, blank=True)
    status = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'sector_master'

    def __str__(self):
        return self.sector_name  
    

class Skill(models.Model):
    id = models.AutoField(primary_key=True)
    skill_code = models.CharField(max_length=50)
    skill_name = models.CharField(max_length=50)
    skill_type = models.SmallIntegerField(null=True, blank=True)
    sector = models.ForeignKey(Sector,on_delete=models.CASCADE,null=True,blank=True,db_column='sector_id')
    doc_required = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_required = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    updated_by = models.IntegerField(null=True, blank=True)
    status = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'skill_master'

    def __str__(self):
        return self.skill_code  
    

class Services(models.Model):
    id = models.BigAutoField(primary_key=True)
    service_name = models.CharField(max_length=255,blank=False,null=True)
    service_code = models.BigIntegerField(blank=False,null=True)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(blank=False)
    is_required = models.BooleanField(default=True)
    mark_as_popular = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=1,blank=False,null=True)
    created_by = models.BigIntegerField(blank=False,null=True)
    created_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)
    updated_by = models.BigIntegerField(blank=False,null=True)
    updated_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)

    class Meta:
        managed = False
        db_table = 'services'


class ParliamentaryConstituency(models.Model):
    id = models.AutoField(primary_key=True)
    pconstituency_name = models.CharField(max_length=50)
    pconstituency_address = models.CharField(max_length=500, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    updated_by = models.IntegerField(null=True, blank=True)
    status = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'parliamentary_constituency'

    def __str__(self):
        return self.constituency_name   


class AssemblyConstituency(models.Model):
    id = models.AutoField(primary_key=True)
    constituency_name = models.CharField(max_length=50)
    constituency_address = models.CharField(max_length=500, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    updated_by = models.IntegerField(null=True, blank=True)
    status = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'assembly_constituency'

    def __str__(self):
        return self.constituency_name
    

class Employer(models.Model):
    id = models.AutoField(primary_key=True)
    employer_name = models.CharField(max_length=50)
    employer_state = models.ForeignKey(State, on_delete=models.CASCADE, null=True, blank=True)
    employer_district = models.ForeignKey(District, on_delete=models.CASCADE, null=True, blank=True)
    contact = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    updated_by = models.IntegerField(null=True, blank=True)
    status = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'employer'

    def __str__(self):
        return self.employer_name
    

class Village(models.Model):
    village_id = models.AutoField(primary_key=True)
    village_name = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    updated_by = models.IntegerField(null=True, blank=True)
    status = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'village_master'

    def __str__(self):
        return self.village_name
    

#! Document Master Data Models =====
class DocumentMaster(models.Model):
    doc_id = models.BigAutoField(primary_key=True)
    upload_doc_type = models.IntegerField(blank=False,null=True)
    doc_name = models.CharField(max_length=255,blank=False,null=True)
    doc_file_type = models.CharField(max_length=255,blank=False,null=True)
    doc_path = models.CharField(max_length=255,blank=False,null=True)
    doc_location = models.CharField(max_length=100,blank=False,null=True)
    ref_id = models.BigIntegerField(blank=False,null=True)
    skill_id = models.BigIntegerField(blank=False,null=True)
    created_by = models.BigIntegerField(blank=False,null=True)
    created_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)
    updated_by = models.BigIntegerField(blank=False,null=True)
    updated_on = models.DateTimeField(blank=False,null=True)
    created_by_type = models.SmallIntegerField(blank=False,null=True)
    updated_by_type = models.SmallIntegerField(blank=False,null=True)
    status = models.SmallIntegerField(default=1,blank=False,null=True)

    class Meta:
        managed = False
        db_table = 'document_master'


class GlobalSearchMaster(models.Model):
    id = models.AutoField(primary_key=True)
    source_type = models.IntegerField(null=True, blank=True)
    source_id = models.BigIntegerField(null=True, blank=True)
    display_name = models.CharField(max_length=255, null=True, blank=True)
    search_text = models.TextField(null=True, blank=True)
    sector= models.ForeignKey(Sector, on_delete=models.CASCADE, null=True, blank=True)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.BigIntegerField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.BigIntegerField(null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)


    class Meta:
        managed = True
        db_table = 'global_search_master'


class SMSTemplate(models.Model):
    id = models.AutoField(primary_key=True)
    template_key = models.CharField(max_length=100, unique=True, blank=False, null=False, help_text="Internal key like OTP_LOGIN, ORDER_CONFIRM")
    template_id = models.CharField(max_length=100, unique=True, blank=False, null=False, help_text="DLT / SMS provider template ID")
    message_body = models.TextField(help_text="SMS message content with placeholders")
    is_active = models.BooleanField(default=True)
    description = models.CharField(max_length=255,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "sms_templates"


class DeviceKeyword(models.Model):
    id = models.BigAutoField(primary_key=True)
    device_uid = models.CharField(max_length=255,db_index=True)
    keyword_name = models.CharField(max_length=100, null=True, blank=True)
    keyword = models.ForeignKey(Services, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(blank=False,null=True)
    updated_on = models.DateTimeField(blank=False,null=True)

    class Meta:
        managed = True
        db_table = "device_keyword"


class TrainingCenter(models.Model):
    id = models.AutoField(primary_key=True)
    training_center_name = models.CharField(max_length=50)
    mpr_id = models.CharField(null=True, blank=True, max_length=50)
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True, blank=True)
    tc_id = models.IntegerField(null=True, blank=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    updated_by = models.IntegerField(null=True, blank=True)
    status = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'training_center'

    def __str__(self):
        return self.training_center_name       


class Batch(models.Model):
    id = models.AutoField(primary_key=True)
    mpr_id = models.CharField(null=True, blank=True, max_length=50)
    batch_code = models.CharField(max_length=100)
    batch_kb_id = models.IntegerField(null=True, blank=True)
    tc = models.ForeignKey(TrainingCenter, on_delete=models.CASCADE, null=True, blank=True)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    updated_by = models.IntegerField(null=True, blank=True)
    status = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'batch_master'
    

#!  FCM Notification Master =====
class FcmNotification(models.Model):
    id = models.AutoField(primary_key=True)
    notification = models.TextField(help_text="SMS message content with placeholders")
    title = models.CharField(max_length=255, null=True, blank=True)
    status = models.SmallIntegerField(blank=False,null=True)
    status_text = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    updated_by = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = "fcm_notification"

