from rest_framework import serializers
from .models import User, Memo
 
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class MemoListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        # Maps for id->instance and id->data item.
        memo_mapping = {memo.id: memo for memo in instance}
        data_mapping = {item['id']: item for item in validated_data}

        # Perform creations and updates.
        ret = []
        for memo_id, data in data_mapping.items():
            memo = memo_mapping.get(memo_id, None)
            if memo is None:
                ret.append(self.child.create(data))
            else:
                ret.append(self.child.update(memo, data))
        return ret

class MemoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        list_serializer_class = MemoListSerializer
        model = Memo
        fields = '__all__'