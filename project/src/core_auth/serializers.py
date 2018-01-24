from rest_framework import serializers
from django.contrib.auth import get_user_model

from oauth2_provider.models import Application
from oauth2_provider.oauth2_backends import OAuthLibCore
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.views.mixins import OAuthLibMixin
from social_django.models import UserSocialAuth
from src.core_auth.models import SocialProfile
from src.utils.fields import PointField

User = get_user_model()

class SocialProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialProfile
        fields = ('provider', 'username')


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
            'picture', 'hobbies', 'social_profiles'
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


class HobbiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('hobbies',)


class LocationSerializer(serializers.ModelSerializer):
    last_location = PointField()

    class Meta:
        model = User
        fields = ('last_location',)

class NearbyUsersSerializer(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name',
            'picture', 'hobbies', 'social_profiles',
            'last_location', 'distance'
        )

    def get_distance(self, obj):
        return obj.distance.mi
