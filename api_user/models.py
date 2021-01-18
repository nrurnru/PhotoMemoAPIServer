from django.db import models
from django.utils import timezone

class User(models.Model):
    objects = models.Manager() #경고없애기용, 무시가능

    user_id = models.CharField(max_length=128, null=False)
    password = models.CharField(max_length=128, null=False)
    address = models.CharField(max_length=256, null=True)
 
    class Meta:
        db_table = "User" #Table이름을 "User"로 설정

class Memo(models.Model):
    objects = models.Manager() #경고없애기용, 무시가능
    
    memo_id = models.ForeignKey(User, on_delete=models.CASCADE)
    memo_number = models.CharField(max_length=128, null = False)
    text = models.TextField()
    createdAt = models.DateTimeField(default=timezone.now)
    updatedAt = models.DateTimeField(default=timezone.now)
    isDeleted = models.BooleanField(default=False)
    isSynced = models.BooleanField(default=False)

