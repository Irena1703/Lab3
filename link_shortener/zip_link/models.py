from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date
import shortuuid as shortid
from django.db import IntegrityError


class Link(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    origin_link = models.URLField()
    zipped_link = models.CharField(max_length=10, unique=True)
    counter = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "[%s]:%s -> %s" % (self.user.username, self.zipped_link, self.origin_link[:30])

    def save(self, *args, **kwargs):
        attempt = 0
        if self.zipped_link != '':
            super().save(*args, **kwargs)
            return
        while True:
            try:
                self.zipped_link = shortid.uuid()[:8]
                super().save(*args, **kwargs)
                return
            except IntegrityError as ex:
                attempt = attempt + 1
                if attempt == 3:
                    raise ex


class Account(models.Model):
    Genders = (
        ('m', 'Male'),
        ('f', 'Female')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    gender = models.CharField(max_length=1, choices=Genders, default='m')
    birth_date = models.DateField(default=date.today)

@receiver(post_save, sender=User)
def update_user_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)
    instance.account.save()
