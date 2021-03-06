import googlemaps

from rest_framework import serializers
from django.conf import settings
from django.contrib.auth import get_user_model

from oauth2_provider.models import Application
from oauth2_provider.oauth2_backends import OAuthLibCore
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.views.mixins import OAuthLibMixin
from social_django.models import UserSocialAuth

from src.connect.models import Connection
from src.pictures.serializers import PictureSerializer
from src.utils.fields import PointField

from src.core_auth.models import AuthError, UserQuerySet

User = get_user_model()

class AuthErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthError
        fields = ('provider', 'message')


class SocialAuthUsernameField(serializers.Field):
    def to_representation(self, obj):
        return obj.get('username')

    def to_internal_value(self, data):
        return {'username': data}


class SocialProfileSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    username = SocialAuthUsernameField(source='extra_data')
    uid = serializers.CharField(read_only=True)
    provider = serializers.CharField(required=False)
    youtube_channel = serializers.SerializerMethodField()
    profile_url = serializers.SerializerMethodField()

    class Meta:
        model = UserSocialAuth
        fields = ('user', 'provider', 'username', 'uid', 'profile_url', 'youtube_channel')

    def get_youtube_channel(self, obj):
        return obj.extra_data.get('youtube_channel')

    def get_profile_url(self, obj):
        return obj.extra_data.get('profile_url')

    def validate_provider(self, value):
        request = self.context['request']
        if request.method == 'POST' and not value:
            raise serializers.ValidationError('This field is required.')

        return value

    def validate(self, data):
        request = self.context['request']
        username = data['extra_data']['username']
        provider = data.get('provider') or self.instance.provider
        already_exists = UserSocialAuth.objects.filter(
            uid=username, provider=provider
        ).exists()
        if already_exists:
            raise serializers.ValidationError(
                'User "{}" already exists in "{}".'.format(username, provider)
            )

        if request.method == 'POST':
            user = data['user']
            already_exists = user.social_auth.filter(provider=provider).exists()
            if already_exists:
                raise serializers.ValidationError(
                    'Social Profile for this user already exists for provider "{}".'.format(
                        provider
                    )
                )

        return data

    def get_username(self, obj):
        return obj.extra_data.get('username')

    def create(self, validated_data):
        validated_data['uid'] = validated_data['extra_data']['username']
        return UserSocialAuth.objects.create(**validated_data)

    def update(self, instance, validated_data):
        username = validated_data['extra_data']['username']
        instance.set_extra_data({'username': username})
        instance.uid = username
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    client_id = serializers.CharField(write_only=True)
    client_secret = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    grant_type = serializers.CharField(write_only=True)
    username = serializers.EmailField(write_only=True)
    email = serializers.EmailField(read_only=True)
    social_profiles = SocialProfileSerializer(read_only=True, many=True, source='social_auth')
    pictures = PictureSerializer(many=True, read_only=True)
    last_location = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'first_name',
            'last_name', 'client_id', 'client_secret', 'grant_type',
            'picture', 'social_profiles', 'hobbies', 'hometown', 'occupation',
            'phone_number', 'age', 'personal_email','ghost_mode',
            'employer', 'age_range', 'bio', 'pictures', 'last_location',
            'address', 'notifications', 'email_is_private', 'phone_is_private',
            'is_random_email', 'tutorial_complete', 'invite_tutorial',
            'connection_tutorial',
        )

    def validate_username(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('User with this email already exists')
        return value

    def validate(self, data):
        try:
            Application.objects.get(
                client_id=data.pop('client_id'),
                client_secret=data.pop('client_secret'),
                authorization_grant_type=data.pop('grant_type')
            )
        except Application.DoesNotExist:
            raise serializers.ValidationError('Application not found.')
        return data

    def get_last_location(self, obj):
        if (not obj.ghost_mode) and obj.last_location:
            return {'lng': obj.last_location.x, 'lat': obj.last_location.y}

    def get_address(self, obj):
        if (not obj.ghost_mode):
            return obj.address

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['email'] = validated_data.pop('username')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class TokenSerializer(serializers.ModelSerializer):
    access_token = serializers.SerializerMethodField()
    expires = serializers.SerializerMethodField()
    auth_time = serializers.SerializerMethodField()

    class Meta:
        model = UserSocialAuth
        fields = ['provider', 'access_token', 'expires', 'auth_time']

    def get_access_token(self, obj):
        extra_data = obj.extra_data
        return extra_data.get('access_token')

    def get_expires(self, obj):
        extra_data = obj.extra_data
        expires = None
        if obj.provider in ['facebook', 'google-oauth2', 'linkedin-oauth2']:
            expires = extra_data.get('expires')
        elif obj.provider == 'twitter':
            expires = extra_data.get('access_token', {}).get('x_auth_expires')

        return expires

    def get_auth_time(self, obj):
        extra_data = obj.extra_data
        return extra_data.get('auth_time')


class ProfileSerializer(serializers.ModelSerializer):
    last_location = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'hobbies', 'hometown', 'occupation',
            'phone_number', 'age', 'personal_email', 'picture',
            'first_name', 'last_name', 'ghost_mode', 'notifications',
            'employer', 'age_range', 'bio',
            'email_is_private', 'phone_is_private', 'last_location', 'address',
        )

    def get_last_location(self, obj):
        if (not obj.ghost_mode) and obj.last_location:
            return {'lng': obj.last_location.x, 'lat': obj.last_location.y}

    def get_address(self, obj):
        if (not obj.ghost_mode):
            return obj.address


class LocationSerializer(serializers.ModelSerializer):
    last_location = PointField(allow_null=True)

    class Meta:
        model = User
        fields = ('last_location',)

    def update(self, instance, validated_data):
        location = self.validated_data['last_location']
        address = None

        if location is not None and instance.last_location != location:
            gmaps = googlemaps.Client(settings.GOOGLE_MAPS_API_KEY)
            address_data = gmaps.reverse_geocode((location.y, location.x))
            formatted = [
                x['formatted_address'] for x in address_data
                if 'locality' in x.get('types', [])
            ]
            if formatted:
                address = formatted[0]
        self.instance.last_location = location
        self.instance.address = address

        instance.save()
        return instance


class TutorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('tutorial_complete', 'invite_tutorial', 'connection_tutorial')


class RetrieveUserSerializer(serializers.ModelSerializer):
    phone_number = serializers.SerializerMethodField()
    personal_email = serializers.SerializerMethodField()
    last_location = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    social_profiles = SocialProfileSerializer(read_only=True, many=True, source='social_auth')
    pictures = PictureSerializer(many=True)

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name',
            'picture', 'social_profiles', 'pictures',
            'hobbies', 'hometown', 'occupation',
            'phone_number', 'age', 'personal_email',
            'employer', 'age_range', 'bio',
            'last_location', 'address'
        )

    def get_phone_number(self, obj):
        if getattr(self.context['request'], 'user') == obj or not obj.phone_is_private:
            if obj.phone_number:
                return str(obj.phone_number)

    def get_personal_email(self, obj):
        if getattr(self.context['request'], 'user') == obj or not obj.email_is_private:
            return obj.personal_email

    def get_last_location(self, obj):
        if (not obj.ghost_mode) and obj.last_location:
            return {'lng': obj.last_location.x, 'lat': obj.last_location.y}

    def get_address(self, obj):
        if (not obj.ghost_mode):
            return obj.address


class NearbyUsersSerializer(RetrieveUserSerializer):
    distance = serializers.SerializerMethodField()
    connection_percentage = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    social_profiles = SocialProfileSerializer(read_only=True, many=True, source='social_auth')
    pictures = PictureSerializer(many=True)

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'featured',
            'picture', 'hobbies', 'social_profiles', 'pictures',
            'last_location', 'address', 'distance',
            'connection_percentage', 'employer', 'age_range',
            'bio', 'hometown', 'phone_number', 'personal_email',
            'category'
        )

    def get_connection_percentage(self, obj):
        return min(100, obj.connection_percentage)

    def get_category(self, obj):
        return UserQuerySet.CATEGORY_CHOICES_MAP[obj.category]

    def get_distance(self, obj):
        if getattr(obj, 'distance', None):
            return obj.distance.mi


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    client_id = serializers.CharField(write_only=True)
    client_secret = serializers.CharField(write_only=True)
    email = serializers.EmailField(read_only=True)
    social_profiles = SocialProfileSerializer(read_only=True, many=True, source='social_auth')

    class Meta:
        model = User
        fields = (
            'new_password', 'old_password', 'client_id',
            'client_secret', 'email', 'social_profiles'
        )

    def validate_old_password(self, value):
        if not self.instance.check_password(value):
            raise serializers.ValidationError('Your old password was entered incorrectly. Please enter it again.')
        return value

    def validate(self, data):
        try:
            Application.objects.get(
                client_id=data.pop('client_id'),
                client_secret=data.pop('client_secret'),
            )
        except Application.DoesNotExist:
            raise serializers.ValidationError('Application not found.')
        return data

    def save(self):
        new_password = self.validated_data['new_password']
        self.instance.set_password(new_password)
        self.instance.save()
