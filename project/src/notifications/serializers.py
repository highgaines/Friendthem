from rest_framework import serializers
from src.notifications.models import Device

class DeviceSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Device
        fields = ('user', 'device_id')

class NotificationSerializer(serializers.ModelSerializer):
    recipient = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        fields = ('sender', 'recipient', 'message')

