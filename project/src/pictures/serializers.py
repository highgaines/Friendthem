from src.pictures.models import UserPicture
from rest_framework import serializers

class PictureSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserPicture
        fields = ('id', 'user', 'url')
