from django.urls import path
from . import views

app_name = 'moneytrack'

urlpatterns = [
    #path('', views.HelloWorldView.as_view(), name='hello_world'),
    path('finance/', views.FinanceListView.as_view(), name='finance_list'),
    path('finance/add_income/', views.AddIncomeView.as_view(), name='add_income'),
    path('finance/add_expense/', views.AddExpenseView.as_view(), name='add_expense'),
    path('accounts/', views.AccountListView.as_view(), name='account_list'),
    path('accounts/add/', views.AddAccountView.as_view(), name='add_account'),

]