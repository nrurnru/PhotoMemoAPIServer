from django.urls import path
from . import views
 
app_name = 'api_user'
urlpatterns = [
    path('', views.UserView.as_view()), # User에 관한 API를 처리하는 view로 Request를 넘김
    path('<int:user_id>', views.UserView.as_view()), # http://localhost:8000/users/{id}

    path('memo/<int:memo_id>', views.MemoView.as_view()), # http://localhost:8000/memo/{id}
    path('memo/', views.MemoView.as_view()), # http://localhost:8000/users/memo/

    path('sync', views.SyncView.as_view()), # http://localhost:8000/users/sync
    path('login', views.LoginView.as_view()), # http://localhost:8000/users/login
]
