from rest_framework import serializers
from django.contrib.auth import get_user_model

from oauth2_provider.models import Application
from oauth2_provider.oauth2_backends import OAuthLibCore
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.views.mixins import OAuthLibMixin

User = get_user_model()

class UserSerializer(OAuthLibMixin, serializers.ModelSerializer):
    server_class = oauth2_settings.OAUTH2_SERVER_CLASS
    validator_class = oauth2_settings.OAUTH2_VALIDATOR_CLASS
    oauthlib_backend_class = OAuthLibCore

    client_id = serializers.CharField(write_only=True)
    client_secret = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    grant_type = serializers.CharField(write_only=True)
    username = serializers.EmailField()

    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name', 'client_id', 'client_secret', 'grant_type')

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
