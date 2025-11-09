from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    # 基本路由 #由上到下觸發，符合就執行對應的 view
    path('', views.HelloWorldView.as_view(), name='hello_world'),
    #path('<str:student_name>/', views.HelloStudentView.as_view(), name='hello_Student'),
    path('jsonresponse/', views.JsonResponseView.as_view(), name='json_response'),
    path('book_list/', views.BookListView.as_view(), name='book_list'),
    path('book/<int:book_id>', views.BookDetailView.as_view(), name='book_detail'),
    path('book_create/', views.BookCreateView.as_view(), name='book_create')

    
]
