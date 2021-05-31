from . import views
from django.urls import path
from django.urls import re_path
from . import consumer

websocket_urlpatterns = [
    re_path(r'chat/ws/$', consumer.ChatConsumer.as_asgi()),
]

urlpatterns = [
    path('<str:link>/send/', views.webhook, name="webhook"),
    path('chat/', views.ChatView.as_view(), name='chat'),
    path('chat/users/', views.ChatUsersView.as_view(), name='chat-users'),
]

