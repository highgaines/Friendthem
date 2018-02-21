from rest_framework import serializers
from src.notifications.models import Device, Notification
from src.core_auth.models import User
from src.core_auth.serializers import RetrieveUserSerializer

class DeviceSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Device
        fields = ('user', 'device_id')

class NotificationSerializer(serializers.ModelSerializer):
    recipient = serializers.HiddenField(default=serializers.CurrentUserDefault())
    sender = RetrieveUserSerializer()

    class Meta:
        model = Notification
        fields = ('sender', 'recipient', 'message',)
