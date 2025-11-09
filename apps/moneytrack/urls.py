from django.urls import path
from . import views

app_name = 'moneytrack'

urlpatterns = [
    path('', views.HelloWorldView.as_view(), name='hello_world'),
    path('finance_list/', views.FinanceListView.as_view(), name='finance_list'),
]