from src.pictures.models import UserPicture
from rest_framework import serializers

class PictureSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserPicture
        fields = ('id', 'user', 'url')

    def validate(self, data):
        if data['user'].pictures.count() >= 6:
            raise serializers.ValidationError(
                'User already has 6 pictures. '
                'You must delete one before adding other.'
            )
        return data
