from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer, MemoSerializer, DeletedMemoIDListSerializer, DeletedMemoIDSerializer
from rest_framework import status
from .models import User, Memo, DeletedMemoID
from rest_framework import request
from django.utils import timezone
from django.db.models import Q
 
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

            user_id = request.META.get('HTTP_AUTHORIZATION')
            query_user_id = Q(user_id = user_id)

            memo_queryset = Memo.objects.filter(query_user_id)
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
        user_id = request.META.get('HTTP_AUTHORIZATION')
        last_synced = request.GET.get("last_synced", None)
        if last_synced is None:
            return Response("error: 'data' parameter needed", status = status.HTTP_400_BAD_REQUEST)

        # 마지막 동기화 날짜 이후 데이터 검색
        query_last_sync = Q(updated_at__gte=last_synced)
        query_user_id = Q(user_id = user_id)
        updated_memo_queryset = Memo.objects.filter(query_last_sync & query_user_id)
        updated_memo_serializer = MemoSerializer(updated_memo_queryset, many = True)

        sync_data = {}
        sync_data['updated_memos'] = updated_memo_serializer.data

        # 삭제한 메모 아이디 반환
        deleted_query = DeletedMemoID.objects.filter(user_id=user_id)
        deleted_serializer = DeletedMemoIDSerializer(deleted_query, many = True)
        deleted_memo_ids = []
        for data in deleted_serializer.data:
            deleted_memo_ids.append(data['deleted_id'])
        sync_data['deleted_memo_ids'] = deleted_memo_ids

        return Response(sync_data, status = status.HTTP_200_OK)

    def post(self, request):
        # 헤더로부터 유저 아이디 전달
        user_id = request.META.get('HTTP_AUTHORIZATION')
        if user_id == None:
            return Response("error: User id required", status = status.HTTP_401_UNAUTHORIZED)
        
        user_object = User.objects.get(user_id = user_id)
        if user_id == None:
            return Response("error: Given wrong id", status = status.HTTP_401_UNAUTHORIZED)

        # 메모 업데이트
        updated_memo_query = Memo.objects.filter(user_id = user_id)
        updated_memo_serializer = MemoSerializer(updated_memo_query, data=request.data['updated_memos'], many=True)
        if updated_memo_serializer.is_valid():
            updated_memo_serializer.save(user_id = user_object)
        else:
            return Response(updated_memo_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # 지워진 메모 ID 리스트 테이블에 추가
        for deleted_memo_id in request.data['deleted_memo_ids']:
            try:
                DeletedMemoID.objects.get(deleted_id=deleted_memo_id)
            except:
                DeletedMemoID.objects.create(user_id=user_object, deleted_id=deleted_memo_id)

        # 메모 테이블에서 지워진 메모를 삭제
        for deleted_memo_id in request.data['deleted_memo_ids']:
            target = Memo.objects.get(id=deleted_memo_id)
            target.delete()

        return Response("Upload sync completed successfully", status=status.HTTP_200_OK)
