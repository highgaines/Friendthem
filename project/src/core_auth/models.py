from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, *args, **kwargs):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    username = None

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class Profile(models.Model):
    hobbies = ArrayField(models.CharField(max_length=64))
    picture = models.URLField()

class SocialProfile(models.Model):
    provider = models.CharField(max_length=32)

    profile = models.ForeignKey(
        'Profile',
        related_name='social_profile',
        on_delete=models.CASCADE,
    )
    username = models.CharField(max_length=256)

    class Meta:
        unique_together = ('profile', 'provider')

    def __str__(self):
        return str(self.user)
