from django.conf.urls import include
from . import views
from django.urls import path
from django.urls import re_path
from . import consumer


websocket_urlpatterns = [
    re_path(r'task/ws/$', consumer.TaskViewConsumer.as_asgi()),
]

urlpatterns = [
    path('admin-task/', views.AdminTaskView.as_view(), name='admin-task'),
    path('account/statistic', views.StatisticDataView.as_view(), name='user-statistic')
]
# 