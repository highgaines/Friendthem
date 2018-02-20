from django.conf import settings
from django.db import models

# Create your models here.
class Connection(models.Model):
    FACEBOOK = 'facebook'
    INSTAGRAM = 'instagram'
    TWITTER = 'twitter'
    YOUTUBE = 'youtube'
    SNAPCHAT = 'snapchat'

    PROVIDER_CHOICES = (
        (FACEBOOK, 'Facebook'),
        (INSTAGRAM, 'Instagram'),
        (YOUTUBE, 'Youtube'),
        (TWITTER, 'Twitter'),
        (SNAPCHAT, 'Snapchat'),
    )

    user_1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='connection_user_1',
        on_delete=models.CASCADE
    )
    user_2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='connection_user_2',
        on_delete=models.CASCADE
    )
    provider = models.CharField(max_length=10, choices=PROVIDER_CHOICES)
    confirmed = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user_1', 'user_2', 'provider')
