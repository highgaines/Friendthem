from unittest.mock import Mock, patch
import pytest
from model_mommy import mommy

from django.test import TestCase
from django.conf import settings
from src.connect.services import TwitterConnect, TwitterCredentialsNotFound, TwitterUserNotFound

class TwitterConnectTestCase(TestCase):
    def setUp(self):
        self.user_social_auth = mommy.make(
            'UserSocialAuth',
            provider='twitter',
            extra_data={'access_token': {
                'oauth_token': 'abcde', 'oauth_token_secret': 'acdbe'
            }})
        self.user = self.user_social_auth.user

        self.other_social_auth = mommy.make(
            'UserSocialAuth',
            provider='twitter',
            uid='123456'
        )
        self.other_user = self.other_social_auth.user

    @patch.object(TwitterConnect, '_authenticate')
    def test_initialization_calls_authenticate_for_user_1(self, authenticate):
        connect = TwitterConnect(self.user)
        authenticate.assert_called_once_with(self.user)

    @patch('src.connect.services.twitter')
    def test_authenticate_calls_api_with_tokens(self, mocked_twitter):
        connect = TwitterConnect(self.user)
        mocked_twitter.Api.assert_called_once_with(
            consumer_key=settings.SOCIAL_AUTH_TWITTER_KEY,
            consumer_secret=settings.SOCIAL_AUTH_TWITTER_SECRET,
            access_token_key='abcde', access_token_secret='acdbe'
        )

    def test_authenticate_raises_error_if_no_user_social_auth(self):
        self.user_social_auth.delete()
        with pytest.raises(TwitterCredentialsNotFound):
            connect = TwitterConnect(self.user)

    def test_authenticate_raises_error_if_no_user_credentials(self):
        self.user_social_auth.extra_data = {}
        self.user_social_auth.save()
        with pytest.raises(TwitterCredentialsNotFound):
            connect = TwitterConnect(self.user)

    @patch('src.connect.services.twitter')
    def test_connect_calls_create_friendship_on_twitter(self, mocked_twitter):
        api_object = Mock()
        friendship = Mock()
        friendship.following = True
        api_object.CreateFriendship.return_value = friendship
        mocked_twitter.Api.return_value = api_object

        connect = TwitterConnect(self.user)
        connection = connect.connect(self.other_user)
        assert connection is True
        api_object.CreateFriendship.assert_called_once_with(
            user_id=self.other_social_auth.uid, follow=True
        )

    @patch('src.connect.services.twitter')
    def test_connect_raises_error_if_user_social_auth_does_not_exist(self, mocked_twitter):
        api_object = Mock()
        friendship = Mock()
        friendship.following = True
        api_object.CreateFriendship.return_value = friendship
        mocked_twitter.Api.return_value = api_object

        self.other_social_auth.delete()

        connect = TwitterConnect(self.user)
        with pytest.raises(TwitterUserNotFound):
            connection = connect.connect(self.other_user)
        api_object.CreateFriendship.assert_not_called()
