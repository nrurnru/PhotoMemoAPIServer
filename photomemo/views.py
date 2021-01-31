import jwt, json, os
from pathlib import Path
from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import ImproperlyConfigured
from rest_framework import status
from rest_framework import request
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User, Memo, DeletedMemoID
from .serializers import UserSerializer, MemoSerializer, DeletedMemoIDListSerializer, DeletedMemoIDSerializer

def get_secret(setting):
    BASE_DIR = Path(__file__).resolve().parent.parent
    secret_file = os.path.join(BASE_DIR, 'config/secrets.json')
    with open(secret_file) as f:
        secrets = json.loads(f.read())
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

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

class SyncView(APIView):
    def get(self, request):
        jwt_data = request.META.get('HTTP_JWT')
        jwt_token = jwt.decode(jwt_data, get_secret('SECRET_KEY'), get_secret('JWT_ALGORITHM'))
        user_id = jwt_token['user_id']
        if user_id is None:
            return Response("error: invalid token", status = status.HTTP_401_UNAUTHORIZED)

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
        # 헤더로부터 jwt 토큰 받아오기
        jwt_data = request.META.get('HTTP_JWT')
        jwt_token = jwt.decode(jwt_data, get_secret('SECRET_KEY'), get_secret('JWT_ALGORITHM'))
        user_id = jwt_token['user_id']
        if user_id is None:
            return Response("error: invalid token", status = status.HTTP_401_UNAUTHORIZED)

        user_object = User.objects.get(user_id = user_id)
        if user_object is None:
            return Response("error: no user match with token", status = status.HTTP_401_UNAUTHORIZED)

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
            try:
                target = Memo.objects.get(id=deleted_memo_id)
                target.delete()
            except:
                pass
            

        return Response("Upload sync completed successfully", status=status.HTTP_200_OK)

class LoginView(APIView):
    def get(self, request):
        user_id = request.META.get('HTTP_USERID')
        password = request.META.get('HTTP_USERPASSWORD')

        if user_id is None or password is None:
            return Response("error: lgin information required.", status = status.HTTP_401_UNAUTHORIZED)

        user_query = User.objects.filter(user_id=user_id, password=password)
        if user_query.exists():
            data = {'user_id': user_id, 'password': password}
            token_data = {'token': jwt.encode(data, get_secret('SECRET_KEY'), get_secret('JWT_ALGORITHM'))}
            return Response(token_data, status = status.HTTP_200_OK)
        else:
            return Response("error: user does not match.", status = status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        user_id = request.META.get('HTTP_USERID')
        user_password = request.META.get('HTTP_USERPASSWORD')
        data = {'user_id': user_id, 'password': user_password}
        user_serializer = UserSerializer(data = data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response("success", status=status.HTTP_201_CREATED)
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)