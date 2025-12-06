from django.urls import path
from . import views

app_name = 'moneytrack'

urlpatterns = [
    #path('', views.HelloWorldView.as_view(), name='hello_world'),
    # finance URLs
    path('finance/', views.FinanceListView.as_view(), name='finance_list'),
    path('finance/add_income/', views.AddIncomeView.as_view(), name='add_income'),
    path('finance/add_expense/', views.AddExpenseView.as_view(), name='add_expense'),
    path('finance/income/<int:pk>/edit/', views.EditIncomeView.as_view(), name='edit_income'),
    path('finance/income/<int:pk>/delete/', views.DeleteIncomeView.as_view(), name='delete_income'),
    path('finance/expense/<int:pk>/edit/', views.EditExpenseView.as_view(), name='edit_expense'),
    path('finance/expense/<int:pk>/delete/', views.DeleteExpenseView.as_view(), name='delete_expense'),

# accounts URLs
    path('accounts/', views.AccountListView.as_view(), name='account_list'),
    path('accounts/add/', views.AddAccountView.as_view(), name='add_account'),
    path('accounts/<int:pk>/edit/', views.EditAccountView.as_view(), name='edit_account'),
    path('accounts/<int:pk>/delete/', views.DeleteAccountView.as_view(), name='delete_account'),
    
# ==================== AJAX API URLs (新增部分) ====================
    path('api/add-income/', views.AddIncomeAPIView.as_view(), name='api_add_income'),
    path('api/add-expense/', views.AddExpenseAPIView.as_view(), name='api_add_expense'),




]