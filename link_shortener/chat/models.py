from django.db import models
from django.contrib.auth.models import User


class ConnectedUsers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    connected = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return "%s connected at %s" % (self.user.username, self.connected)