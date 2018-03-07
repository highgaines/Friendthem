from rest_framework import serializers
from django.contrib.auth import get_user_model

from oauth2_provider.models import Application
from oauth2_provider.oauth2_backends import OAuthLibCore
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.views.mixins import OAuthLibMixin
from social_django.models import UserSocialAuth
from src.connect.models import Connection
from src.core_auth.models import SocialProfile, AuthError
from src.utils.fields import PointField

User = get_user_model()

class AuthErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthError
        fields = ('provider', 'message')

class SocialProfileSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    uid = serializers.SerializerMethodField()

    class Meta:
        model = SocialProfile
        fields = ('user', 'provider', 'username', 'uid')

    def get_uid(self, obj):
        provider = obj.provider
        user_social_auth = obj.user.social_auth.filter(provider=provider)

        if len(user_social_auth):
            provider_uid = user_social_auth[0].uid
        else:
            provider_uid = None

        return provider_uid


class UserSerializer(serializers.ModelSerializer):
    client_id = serializers.CharField(write_only=True)
    client_secret = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    grant_type = serializers.CharField(write_only=True)
    username = serializers.EmailField(write_only=True)
    email = serializers.EmailField(read_only=True)
    social_profiles = SocialProfileSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'first_name',
            'last_name', 'client_id', 'client_secret', 'grant_type',
            'picture', 'social_profiles', 'hobbies', 'hometown', 'occupation',
            'phone_number', 'age', 'personal_email','ghost_mode',
            'employer', 'age_range', 'bio',
            'notifications', 'email_is_private', 'phone_is_private',
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

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['username']
        )
        user.set_password(validated_data['password'])
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
    class Meta:
        model = User
        fields = (
            'hobbies', 'hometown', 'occupation',
            'phone_number', 'age', 'personal_email', 'picture',
            'first_name', 'last_name', 'ghost_mode', 'notifications',
            'employer', 'age_range', 'bio',
            'email_is_private', 'phone_is_private',
        )


class LocationSerializer(serializers.ModelSerializer):
    last_location = PointField(allow_null=True)

    class Meta:
        model = User
        fields = ('last_location',)


class RetrieveUserSerializer(serializers.ModelSerializer):
    phone_number = serializers.SerializerMethodField()
    personal_email = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name',
            'picture', 'social_profiles',
            'hobbies', 'hometown', 'occupation',
            'phone_number', 'age', 'personal_email',
            'employer', 'age_range', 'bio',
        )

    def get_phone_number(self, obj):
        if getattr(self.context['request'], 'user') == obj or not obj.phone_is_private:
            if obj.phone_number:
                return str(obj.phone_number)

    def get_personal_email(self, obj):
        if getattr(self.context['request'], 'user') == obj or not obj.email_is_private:
            return obj.personal_email

class ConnectionPercentageMixin(object):
    connection_percentage = serializers.SerializerMethodField()

    def get_connection_percentage(self, obj):
        user_1 = self.context['request'].user
        user_2 = obj
        percentage = 0
        if user_2.social_profiles.count() or user_1.social_profiles.count():
            percentage = (
                Connection.objects.filter(
                    user_1=user_1, user_2=user_2
                ).count() / min(
                    max(1, user_1.social_profiles.count()),
                    max(1, user_2.social_profiles.count())
                )
            )

        return round(percentage * 100)


class NearbyUsersSerializer(ConnectionPercentageMixin, RetrieveUserSerializer):
    distance = serializers.SerializerMethodField()
    connection_percentage = serializers.SerializerMethodField()
    social_profiles = SocialProfileSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'featured',
            'picture', 'hobbies', 'social_profiles',
            'last_location', 'distance', 'connection_percentage',
            'employer', 'age_range', 'bio', 'hometown',
            'phone_number', 'personal_email'
        )

    def get_distance(self, obj):
        if getattr(obj, 'distance', None):
            return obj.distance.mi


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    client_id = serializers.CharField(write_only=True)
    client_secret = serializers.CharField(write_only=True)
    email = serializers.EmailField(read_only=True)
    social_profiles = SocialProfileSerializer(read_only=True, many=True)

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
