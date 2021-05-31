import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import ConnectedUsers


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = "user"
        self.room_group_name = 'chat_%s' % self.room_name
        if self.scope['user'] == "":
            return

        isUser = ConnectedUsers.objects.filter(user = self.scope['user'])

        if isUser.count() != 0:
            return

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.user = self.scope["user"]
        ConnectedUsers.objects.create(user=self.user)
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        if not hasattr(self, "user"):
            return

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        ConnectedUsers.objects.filter(user=self.user).delete()

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'name': self.user.username
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            "name": event['name'] if event['name'] != self.user.username else "Me",
            'type' : "chat_message",
            'message': message
        }))

    def chat_link(self, event):
        self.send(json.dumps({
            'type' : "chat_link",
            "origin_link": event['origin_link'],
            "zipped_link": event['zipped_link'],
            "counter": event['counter'],
            "name": event['name'] if event['name'] != self.user.username else "Me",
        })) 