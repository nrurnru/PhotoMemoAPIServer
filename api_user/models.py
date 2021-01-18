from django.db import models
 
class User(models.Model):
    objects = models.Manager() #경고없애기용, 무시가능
    user_id = models.CharField(max_length=128, null=False)
    password = models.CharField(max_length=128, null=False)
    address = models.CharField(max_length=256, null=True)
 
    class Meta:
        db_table = "User" #Table이름을 "User"로 설정