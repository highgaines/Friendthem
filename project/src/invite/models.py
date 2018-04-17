from django.conf import settings
from django.db import models

from phonenumber_field.modelfields import PhoneNumberField

class Invite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = PhoneNumberField()

    class Meta:
        unique_together = ('user', 'phone_number')
