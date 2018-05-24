from rest_framework import serializers
from src.invite.models import Invite

class InviteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Invite
        fields = ('user', 'phone_number')
