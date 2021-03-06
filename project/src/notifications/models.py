from django.conf import settings
from django.db import models

class Device(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    device_id = models.UUIDField(max_length=36)
    created_at = models.DateTimeField(auto_now_add=True)

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
    created_at = models.DateTimeField(auto_now_add=True)
