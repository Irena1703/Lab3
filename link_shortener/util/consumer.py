import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer




class TaskViewConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'tasks'

        if not self.scope["user"].is_staff:
            return
        
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def task(self, event):
        self.send(json.dumps({
                "name" : event["name"],
                "args" :event["args"],
                "result" : event["result"],
                "time" : event["time"], 
        }))

 