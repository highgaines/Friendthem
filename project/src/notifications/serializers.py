from rest_framework import serializers
from src.notifications.models import Device, Notification
from src.core_auth.models import User
from src.core_auth.serializers import UserSerializer

class DeviceSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Device
        fields = ('user', 'device_id')

class NotificationSerializer(serializers.ModelSerializer):
    recipient = serializers.HiddenField(default=serializers.CurrentUserDefault())
    sender = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Notification
        fields = ('sender', 'recipient', 'message',)

    def get_sender(self, obj):
        return UserSerializer(User.objects.get(id=obj.sender_id)).data