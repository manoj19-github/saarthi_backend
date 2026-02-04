from django.db import models

# Create your models here.

class UserToken(models.Model):
    token_id = models.BigAutoField(primary_key=True)
    user_id = models.BigIntegerField(blank=False,null=True)
    user_type = models.IntegerField(blank=False,null=True)
    token = models.CharField(max_length=500)
    updated_on = models.DateTimeField(blank=False,null=True)
    expiry_time = models.DateTimeField(blank=False,null=True)
    c_m_no = models.CharField(max_length=15,blank=False,null=True)
    allow_flag = models.IntegerField(default=1,blank=False,null=True)

    class Meta:
        managed = True
        db_table = "user_token"
        
        
class FcmToken(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.BigIntegerField(blank=False,null=True)
    user_type = models.IntegerField(blank=False,null=True)
    token = models.CharField(max_length=500)
    device_type = models.CharField(max_length=20,blank=False,null=True)  # android / ios / web
    created_on = models.DateTimeField(blank=False,null=True)
    created_by = models.BigIntegerField(blank=False,null=True)
    updated_on = models.DateTimeField(blank=False,null=True)
    updated_by = models.BigIntegerField(blank=False,null=True)
    expiry_time = models.DateTimeField(blank=False,null=True)
    c_m_no = models.CharField(max_length=15,blank=False,null=True)
    allow_flag = models.IntegerField(default=1,blank=False,null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = "fcm_token"


class FcmJson(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100,blank=False,null=True)
    json = models.JSONField() 
    created_on = models.DateTimeField(auto_now_add=True,blank=False,null=True)
    updated_on = models.DateTimeField(blank=False,null=True)
    created_by = models.IntegerField(blank=False,null=True)
    updated_by = models.IntegerField(blank=False,null=True)
    is_active = models.BooleanField(default=True)
    status = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'fcm_json'

