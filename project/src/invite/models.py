from django.conf import settings
from django.db import models

from phonenumber_field.modelfields import PhoneNumberField

class Invite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    device_id = models.UUIDField(max_length=36)

    class Meta:
        unique_together = ('user', 'device_id')
