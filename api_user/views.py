from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer, MemoSerializer
from rest_framework import status
from .models import User, Memo
from rest_framework import request
from django.utils import timezone
 
class UserView(APIView):
    def get(self, request, **kwargs):
        if kwargs.get('user_id') is None:
            user_queryset = User.objects.all()
            user_queryset_serializer = UserSerializer(user_queryset, many = True)
            return Response(user_queryset_serializer.data, status = status.HTTP_200_OK)
        else:
            user_id = kwargs.get('user_id')
            user_object = User.objects.get(id = user_id)
            user_serializer = UserSerializer(user_object)
            return Response(user_serializer.data, status = status.HTTP_200_OK)

    def post(self, request):
        user_serializer = UserSerializer(data = request.data)

        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        return Response("Not implemented", status=status.HTTP_501_NOT_IMPLEMENTED) 
    
    def delete(self, request):
        return Response("Not implemented", status=status.HTTP_501_NOT_IMPLEMENTED)

class MemoView(APIView):
    def get(self, request, **kwargs):
        if kwargs.get('memo_id') is None:
            memo_queryset = Memo.objects.all()
            memo_queryset_serializer = MemoSerializer(memo_queryset, many = True)
            return Response(memo_queryset_serializer.data, status = status.HTTP_200_OK)
        else:
            memo_id = kwargs.get('memo_id')
            memo_object = Memo.objects.get(id = memo_id)
            memo_serializer = MemoSerializer(memo_object)
            return Response(memo_serializer.data, status = status.HTTP_200_OK)

    def post(self, request):
        memo_serializer = MemoSerializer(data = request.data)
        
        if memo_serializer.is_valid():
            memo_serializer.save()
            return Response(memo_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(memo_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        return Response("Not implemented", status=status.HTTP_501_NOT_IMPLEMENTED) 
    
    def delete(self, request):
        return Response("Not implemented", status=status.HTTP_501_NOT_IMPLEMENTED)

class SyncView(APIView):
    def get(self, request):

        last_synced = request.GET.get("last_synced", None)
        if last_synced is None:
            return Response("error: 'data' parameter needed", status = status.HTTP_400_BAD_REQUEST)

        updated_memo_object = Memo.objects.filter(updated_at__gt=last_synced) 
        updated_memo_serializer = MemoSerializer(updated_memo_object, many=True)

        sync_data = {}
        sync_data['updated_memos'] = updated_memo_serializer.data

        # 삭제한 메모 아이디 구현 필요
        sync_data['deleted_memo_ids'] = ["1","2","3","4"]

        return Response(sync_data, status = status.HTTP_200_OK)

    def post(self, request):

        last_synced = request.data['last_synced']
        memo_object = Memo.objects.filter(updated_at__gt=last_synced)
        updated_memo_serializer = MemoSerializer(memo_object, data=request.data['updated_memos'], many=True)
        if updated_memo_serializer.is_valid():
            updated_memo_serializer.save()
        else:
            return Response(updated_memo_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        #delete 동기화 동작
        pass

        return Response("success", status=status.HTTP_201_CREATED)