from rest_framework import serializers
from src.connect.models import Connection
from src.connect import services

class ConnectionSerializer(serializers.ModelSerializer):
    user_1 = serializers.HiddenField(default=serializers.CurrentUserDefault())
    confirmed = serializers.BooleanField(read_only=True)

    class Meta:
        model = Connection
        fields = ('user_1', 'user_2', 'provider', 'confirmed')

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
