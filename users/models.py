from django.db import models



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


