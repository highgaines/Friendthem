from facebook import GraphAPIError
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.db.models import PointField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField

from src.pictures.services import FacebookProfilePicture
from src.pictures.exceptions import ProfilePicturesAlbumNotFound

class UserQuerySet(models.QuerySet):
    SENT = 1
    RECEIVED = 2
    BOTH = 3
    NOTHING = 0
    CATEGORY_CHOICES_MAP = {
        SENT: 'sent',
        RECEIVED: 'received',
        BOTH: 'both',
        NOTHING: 'nothing',
    }

    def with_connection_percentage_for_user(self, user):
        user_social_count = user.social_auth.count()
        qs = self.exclude(id=user.id).annotate(
            sent_connections_count=models.Count(
                'connection_user_2', filter=models.Q(connection_user_2__user_1=user)
            ),
            received_connections_count=models.Count(
                'connection_user_1', filter=models.Q(connection_user_1__user_2=user)
            ),
            category=models.Case(
                models.When(
                    models.Q(sent_connections_count__gte=1) & \
                    models.Q(received_connections_count=0), then=UserQuerySet.SENT
                ),
                models.When(
                    models.Q(received_connections_count__gte=1) & \
                    models.Q(sent_connections_count=0), then=UserQuerySet.RECEIVED
                ),
                models.When(
                    models.Q(sent_connections_count__gte=1) & \
                    models.Q(received_connections_count__gte=1), then=UserQuerySet.BOTH
                ),
                default=UserQuerySet.NOTHING,
                output_field=models.CharField(max_length=10)
            )
        ).distinct()
        qs = qs.annotate(
            social_count=models.Count('social_auth'),
            connection_percentage=models.Case(
                models.When(
                    category=UserQuerySet.BOTH,
                    then=(
                        models.F('received_connections_count') + \
                        models.F('sent_connections_count')
                    ) * 100. / (models.F('social_count') + user_social_count)
                ),
                models.When(
                    category=UserQuerySet.RECEIVED,
                    then=models.F('received_connections_count') * 100. / user_social_count),
                models.When(
                    category=UserQuerySet.SENT,
                    then=models.F('sent_connections_count') * 100. / models.F('social_count')),
                default=0,
                output_field=models.IntegerField()
            )
          )

        return qs

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
            **kwargs
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

    # Profile
    picture = models.URLField(blank=True, null=True)
    hobbies = ArrayField(models.CharField(max_length=64), blank=True, null=True)
    hometown = models.CharField(max_length=128, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    occupation = models.CharField(max_length=128, blank=True, null=True)
    employer = models.CharField(max_length=128, blank=True, null=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    age_range = models.CharField(max_length=10, blank=True, null=True)
    personal_email = models.EmailField(blank=True, null=True)

    # Settings
    ghost_mode = models.BooleanField(default=False)
    notifications = models.BooleanField(default=True)

    tutorial_complete = models.BooleanField(default=False)
    invite_tutorial = models.BooleanField(default=False)
    connection_tutorial = models.BooleanField(default=False)

    last_location = PointField(
        geography=True, blank=True, null=True,
        help_text="Represented as (longitude, latitude)"
    )
    address = models.CharField(max_length=256, blank=True, null=True)

    featured = models.BooleanField(default=False)
    phone_is_private = models.BooleanField(default=False)
    email_is_private = models.BooleanField(default=False)
    is_random_email = models.BooleanField(default=False)

    objects = UserManager.from_queryset(UserQuerySet)()


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if not self.personal_email and not self.is_random_email:
            self.personal_email = self.email
        return super(User, self).save(*args, **kwargs)


class AuthError(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='auth_errors'
    )
    provider = models.CharField(max_length=32)
    message = models.TextField()


@receiver(post_save, sender=User, dispatch_uid='pull_profile_pictures')
def pull_profile_pictures_from_facebook(sender, instance, **kwargs):
    facebook_auths = instance.social_auth.filter(provider='facebook')
    if instance.featured and facebook_auths and not instance.pictures.all():
        try:
            uid = facebook_auths[0].uid
            service = FacebookProfilePicture(
                access_token='{}|{}'.format(
                    settings.SOCIAL_AUTH_FACEBOOK_KEY,
                    settings.SOCIAL_AUTH_FACEBOOK_SECRET
                )
            )
            pictures = service.get_pictures(uid=uid)[:6]
            picture_objs = [
                instance.pictures.create(url=picture['picture'])
                for picture in pictures
            ]
        except (ProfilePicturesAlbumNotFound, GraphAPIError):
            pass
