from django.conf import settings
from django.db import models

class Device(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=64)

class Notification(models.Model):
    message = models.TextField()
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_notifications',
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_notifications',
        on_delete=models.CASCADE,
        blank=True, null=True
    )
