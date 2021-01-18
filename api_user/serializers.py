from rest_framework import serializers
from .models import User, Memo
 
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class MemoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Memo
        fields = '__all__'
