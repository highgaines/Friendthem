from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.db.models import PointField
from django.db import models
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField

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

    picture = models.URLField(blank=True, null=True)
    hobbies = ArrayField(models.CharField(max_length=64), blank=True, null=True)
    hometown = models.CharField(max_length=128, blank=True, null=True)
    occupation = models.CharField(max_length=128, blank=True, null=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    personal_email = models.EmailField(blank=True, null=True)

    last_location = PointField(
        geography=True, blank=True, null=True,
        help_text="Represented as (longitude, latitude)"
    )

    objects = UserManager()


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class SocialProfile(models.Model):
    provider = models.CharField(max_length=32)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='social_profiles',
        on_delete=models.CASCADE,
    )
    username = models.CharField(max_length=256)

    class Meta:
        unique_together = ('user', 'provider')

    def __str__(self):
        return str(self.user)
