from django.conf import settings
from django.db import models

class UserPicture(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='pictures', on_delete=models.CASCADE
    )
    url = models.URLField()
