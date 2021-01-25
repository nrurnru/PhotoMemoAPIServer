from django.db import models
from django.utils import timezone

class User(models.Model):
    objects = models.Manager() #경고없애기용, 무시가능

    user_id = models.CharField(max_length=256, null=False, primary_key=True)
    password = models.CharField(max_length=256, null=False)
 
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

class DeletedMemoID(models.Model):
    objects = models.Manager()

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    deleted_id = models.CharField(max_length=256, primary_key=True)