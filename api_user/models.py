from django.db import models
from django.utils import timezone

class User(models.Model):
    objects = models.Manager() #경고없애기용, 무시가능

    user_id = models.IntegerField()
    password = models.CharField(max_length=128, null=False)
    address = models.CharField(max_length=256, null=True)
 
    class Meta:
        db_table = "User" #Table이름을 "User"로 설정

class Memo(models.Model):
    objects = models.Manager() #경고없애기용, 무시가능
    
    id = models.CharField(max_length=256, null = False, primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "Memo"