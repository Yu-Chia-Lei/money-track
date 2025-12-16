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

# 統計API URLs
    path('api/chart-data/', views.ChartDataAPI.as_view(), name='api_chart_data'),

# 圖表頁面
    path('charts/', views.ChartsPageView.as_view(), name='charts_view'),

# # AJAX API 端點
    path('api/expense/delete/<int:pk>/', views.delete_expense_ajax, name='delete_expense_ajax'),
    path('api/income/delete/<int:pk>/', views.delete_income_ajax, name='delete_income_ajax'),
    path('api/account/delete/<int:pk>/', views.DeleteAccountAjaxView.as_view(), name='delete_account_ajax'),
    path('api/transactions/filter/', views.TransactionFilterApiView.as_view(), name='transaction_filter_api'),
]

