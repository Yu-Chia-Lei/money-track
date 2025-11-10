from django.urls import path
from . import views

app_name = 'charts'

urlpatterns = [
    path('', views.charts_home.as_view(), name='chart_home'),
]