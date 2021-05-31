

from django.contrib.auth.models import User
from django.db import models


class UserTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task_id = models.CharField(max_length=36)
    task_end = models.DateTimeField()

    pass
