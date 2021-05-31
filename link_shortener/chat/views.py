from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls.base import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from channels.layers import get_channel_layer
from zip_link.models import Link
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from asgiref.sync import async_to_sync
from .models import ConnectedUsers

class ChatView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('login')
    template_name = 'zip_link/chat.html'
    title = 'chat'

class ChatUsersView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    login_url = reverse_lazy('login')
    template_name = 'zip_link/chat-users.html'
    title = 'chat-users'   
    paginate_by = 5

    def get_queryset(self):
        queryset = ConnectedUsers.objects.all().order_by('-connected')
        return queryset

    def test_func(self):
        return self.request.user.is_staff 
    

def webhook(request, link):
    object = get_object_or_404(Link, origin_link=link)
    if request.user != object.user:
        raise PermissionDenied 
    channel_layer = get_channel_layer()
    if not channel_layer.groups:
        return HttpResponse('No any groups available')
    async_to_sync(channel_layer.group_send)(
        list(channel_layer.groups.keys())[0], {
            'type' : "chat_link",
            "origin_link": object.origin_link,
            "zipped_link": object.zipped_link,
            "counter": object.counter,
            "name": request.user.username,
        })
    return HttpResponse("Send in chat")