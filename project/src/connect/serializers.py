from rest_framework import serializers

from django.contrib.auth import get_user_model
from src.core_auth.serializers import (ConnectionPercentageMixin,
                                       RetrieveUserSerializer,
                                       SocialProfileSerializer)
from src.notifications.services import notify_user

from src.connect.models import Connection
from src.connect import services


User = get_user_model()

class ConnectionSerializer(serializers.ModelSerializer):
    user_1 = serializers.HiddenField(default=serializers.CurrentUserDefault())
    user_2_data = RetrieveUserSerializer(source='user_2', read_only=True)
    confirmed = serializers.BooleanField(read_only=True)
    notified = serializers.SerializerMethodField()

    class Meta:
        model = Connection
        fields = ('user_1', 'user_2', 'provider', 'confirmed', 'notified', 'user_2_data')

    def _get_connect_class(self, provider):
        return getattr(
            services,
            '{}Connect'.format(provider.capitalize()),
            services.DummyConnect
        )

    def validate(self, data):
        connect_class = self._get_connect_class(data['provider'])
        try:
            connect = connect_class(data['user_1'])
            confirmed = connect.connect(data['user_2'])
        except Exception as err:
            raise serializers.ValidationError(getattr(err, 'message', str(err)))

        data['confirmed'] = confirmed
        return data

    def get_notified(self, obj):
        msg = '{} wants to connect with you. Would you like to return?'.format(
            obj.user_1.get_full_name()
        )

        try:
            return notify_user(obj.user_1, obj.user_2, msg)
        except:
            return False

class ConnectedUserSerializer(ConnectionPercentageMixin, RetrieveUserSerializer):
    connection_percentage = serializers.SerializerMethodField()
    social_profiles = SocialProfileSerializer(many=True)

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'featured',
            'picture', 'hobbies', 'social_profiles',
            'connection_percentage', 'employer', 'age_range', 'bio',
            'phone_number', 'personal_email'
        )
