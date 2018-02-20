from unittest.mock import Mock, patch
from model_mommy import mommy

from rest_framework.test import APITestCase
from src.connect.serializers import ConnectionSerializer
from src.connect.models import Connection
from src.connect.exceptions import CredentialsNotFound

class ConnectionSerializerTestCase(APITestCase):
    def test_serializer_validation_passes_and_creates_object_for_facebook(self):
        social_1 = mommy.make('UserSocialAuth')
        user_1 = social_1.user
        social_2 = mommy.make('UserSocialAuth')
        user_2 = social_2.user

        request = Mock()
        request.user = user_1

        serializer = ConnectionSerializer(
            data={'user_2': user_2.id, 'provider': 'facebook'}, context={'request': request}
        )
        assert serializer.is_valid() is True
        serializer.save()
        connection = Connection.objects.get(
            user_1=user_1, user_2=user_2, provider='facebook'
        )
        assert connection.confirmed is False

    def test_serializer_validation_dont_pass_for_invalid_provider(self):
        social_1 = mommy.make('UserSocialAuth')
        user_1 = social_1.user
        social_2 = mommy.make('UserSocialAuth')
        user_2 = social_2.user

        request = Mock()
        request.user = user_1

        serializer = ConnectionSerializer(
            data={'user_2': user_2.id, 'provider': 'provider'}, context={'request': request}
        )
        assert serializer.is_valid() is False
        assert serializer.errors['provider'][0] == '"provider" is not a valid choice.'

    @patch('src.connect.serializers.services')
    @patch('src.connect.serializers.notify_user')
    def test_return_notified_false_if_error_on_notification(self, mocked_notify, mocked_services):
        mocked_notify.side_effect = Exception()
        youtube_connect = Mock()
        youtube_connect.connect.return_value = True
        mocked_services.YoutubeConnect.return_value = youtube_connect

        social_1 = mommy.make('UserSocialAuth')
        user_1 = social_1.user
        social_2 = mommy.make('UserSocialAuth')
        user_2 = social_2.user

        request = Mock()
        request.user = user_1

        serializer = ConnectionSerializer(
            data={'user_2': user_2.id, 'provider': 'youtube'}, context={'request': request}
        )
        assert serializer.is_valid() is True
        connection = serializer.save()
        assert serializer.data == {'user_2': user_2.id, 'provider': 'youtube', 'confirmed': True, 'notified': False}

        mocked_services.YoutubeConnect.assert_called_once_with(user_1)
        youtube_connect.connect.assert_called_once_with(user_2)

        mocked_notify.assert_called_once_with(user_1, user_2, '{} wants to connect with you. Would you like to return?'.format(user_1.get_full_name()))


    @patch('src.connect.serializers.services')
    @patch('src.connect.serializers.notify_user')
    def test_serializer_validation_calls_service_connect_for_youtube(self, mocked_notify, mocked_services):
        mocked_notify.return_value = True
        youtube_connect = Mock()
        youtube_connect.connect.return_value = True
        mocked_services.YoutubeConnect.return_value = youtube_connect

        social_1 = mommy.make('UserSocialAuth')
        user_1 = social_1.user
        social_2 = mommy.make('UserSocialAuth')
        user_2 = social_2.user

        request = Mock()
        request.user = user_1

        serializer = ConnectionSerializer(
            data={'user_2': user_2.id, 'provider': 'youtube'}, context={'request': request}
        )
        assert serializer.is_valid() is True
        connection = serializer.save()
        assert serializer.data == {'user_2': user_2.id, 'provider': 'youtube', 'confirmed': True, 'notified': True}

        mocked_services.YoutubeConnect.assert_called_once_with(user_1)
        youtube_connect.connect.assert_called_once_with(user_2)

        mocked_notify.assert_called_once_with(user_1, user_2, '{} wants to connect with you. Would you like to return?'.format(user_1.get_full_name()))

    @patch('src.connect.serializers.services')
    def test_serializer_validation_raises_error_for_service_error(self, mocked_services):
        social_1 = mommy.make('UserSocialAuth')
        user_1 = social_1.user
        social_2 = mommy.make('UserSocialAuth')
        user_2 = social_2.user

        youtube_connect = Mock()
        youtube_connect.side_effect = CredentialsNotFound('youtube', user_1)
        mocked_services.YoutubeConnect = youtube_connect

        request = Mock()
        request.user = user_1

        serializer = ConnectionSerializer(
            data={'user_2': user_2.id, 'provider': 'youtube'}, context={'request': request}
        )
        assert serializer.is_valid() is False
        assert serializer.errors == {'non_field_errors': ['Credentials not found for user "{}" in provider "youtube".'.format(user_1.id)]}
