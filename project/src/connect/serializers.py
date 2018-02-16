from rest_framework import serializers
from src.connect.models import Connection
from src.core_auth.models import User
from src.connect import services
from src.notifications.services import notify_user

class ConnectionSerializer(serializers.ModelSerializer):
    user_1 = serializers.HiddenField(default=serializers.CurrentUserDefault())
    confirmed = serializers.BooleanField(read_only=True)
    notified = serializers.SerializerMethodField()

    class Meta:
        model = Connection
        fields = ('user_1', 'user_2', 'provider', 'confirmed', 'notified')

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
            raise serializers.ValidationError(err.message)

        data['confirmed'] = confirmed
        return data

    def get_notified(self, data):
        user_1 = User.objects.get(id=data.user_1_id)
        user_2 = User.objects.get(id=data.user_2_id)
        msg = '{} wants to connect with you. Would you like to return?'.format(
            user_1.get_full_name()
        )

        try:
            return notify_user(user_1, user_2, msg)
        except:
            return False
