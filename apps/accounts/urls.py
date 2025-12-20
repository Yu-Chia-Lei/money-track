"""
使用者帳號相關 URL 路由
"""
from django.urls import path
from apps.accounts import views

app_name = 'accounts'

urlpatterns = [
    path('preference/', views.profile_settings, name='profile_settings'),
]