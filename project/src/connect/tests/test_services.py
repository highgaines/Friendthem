from unittest.mock import Mock, patch
import pytest
from model_mommy import mommy

from django.test import TestCase
from django.conf import settings
from src.connect.services import TwitterConnect, InstagramConnect, YoutubeConnect
from src.connect.exceptions import CredentialsNotFound, SocialUserNotFound

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

    @patch('src.connect.services.twitter.twitter')
    def test_authenticate_calls_api_with_tokens(self, mocked_twitter):
        connect = TwitterConnect(self.user)
        mocked_twitter.Api.assert_called_once_with(
            consumer_key=settings.SOCIAL_AUTH_TWITTER_KEY,
            consumer_secret=settings.SOCIAL_AUTH_TWITTER_SECRET,
            access_token_key='abcde', access_token_secret='acdbe'
        )

    def test_authenticate_raises_error_if_no_user_social_auth(self):
        self.user_social_auth.delete()
        with pytest.raises(CredentialsNotFound):
            connect = TwitterConnect(self.user)

    def test_authenticate_raises_error_if_no_user_credentials(self):
        self.user_social_auth.extra_data = {}
        self.user_social_auth.save()
        with pytest.raises(CredentialsNotFound):
            connect = TwitterConnect(self.user)

    @patch('src.connect.services.twitter.twitter')
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

    @patch('src.connect.services.twitter.twitter')
    def test_connect_calls_create_unconfirmed_friendship_on_twitter(self, mocked_twitter):
        api_object = Mock()
        friendship = Mock()
        friendship.following = False
        api_object.CreateFriendship.return_value = friendship
        mocked_twitter.Api.return_value = api_object

        connect = TwitterConnect(self.user)
        connection = connect.connect(self.other_user)
        assert connection is False
        api_object.CreateFriendship.assert_called_once_with(
            user_id=self.other_social_auth.uid, follow=True
        )

    @patch('src.connect.services.twitter.twitter')
    def test_connect_raises_error_if_user_social_auth_does_not_exist(self, mocked_twitter):
        api_object = Mock()
        friendship = Mock()
        friendship.following = True
        api_object.CreateFriendship.return_value = friendship
        mocked_twitter.Api.return_value = api_object

        self.other_social_auth.delete()

        connect = TwitterConnect(self.user)
        with pytest.raises(SocialUserNotFound):
            connection = connect.connect(self.other_user)
        api_object.CreateFriendship.assert_not_called()


class InstagramConnectTestCase(TestCase):
    def setUp(self):
        self.user_social_auth = mommy.make(
            'UserSocialAuth',
            provider='instagram',
            extra_data={'access_token': '123456'}
        )
        self.user = self.user_social_auth.user

        self.other_social_auth = mommy.make(
            'UserSocialAuth',
            provider='instagram',
            uid='123456'
        )
        self.other_user = self.other_social_auth.user

    @patch.object(InstagramConnect, '_authenticate')
    def test_initialization_calls_authenticate_for_user_1(self, authenticate):
        connect = InstagramConnect(self.user)
        authenticate.assert_called_once_with(self.user)

    @patch('src.connect.services.instagram.InstagramAPI')
    def test_authenticate_calls_api_with_tokens(self, mocked_instagram):
        connect = InstagramConnect(self.user)
        mocked_instagram.assert_called_once_with(
            client_secret=settings.SOCIAL_AUTH_INSTAGRAM_SECRET,
            access_token='123456'
        )

    def test_authenticate_raises_error_if_no_user_social_auth(self):
        self.user_social_auth.delete()
        with pytest.raises(CredentialsNotFound):
            connect = InstagramConnect(self.user)

    def test_authenticate_raises_error_if_no_user_credentials(self):
        self.user_social_auth.extra_data = {}
        self.user_social_auth.save()
        with pytest.raises(CredentialsNotFound):
            connect = InstagramConnect(self.user)

    @patch('src.connect.services.instagram.InstagramAPI')
    def test_connect_calls_creates_follow_on_instagram(self, mocked_instagram):
        api_object = Mock()
        follow = [Mock()]
        follow[0].outgoing_status = 'follows'
        api_object.follow_user.return_value = follow
        mocked_instagram.return_value = api_object

        connect = InstagramConnect(self.user)
        connection = connect.connect(self.other_user)
        assert connection is True
        api_object.follow_user.assert_called_once_with(
            user_id=self.other_social_auth.uid,
        )

    @patch('src.connect.services.instagram.InstagramAPI')
    def test_connect_calls_creates_unconfirmed_follow_on_instagram(self, mocked_instagram):
        api_object = Mock()
        follow = [Mock()]
        follow[0].outgoing_status = 'unconfirmed'
        api_object.follow_user.return_value = follow
        mocked_instagram.return_value = api_object

        connect = InstagramConnect(self.user)
        connection = connect.connect(self.other_user)
        assert connection is False
        api_object.follow_user.assert_called_once_with(
            user_id=self.other_social_auth.uid,
        )

    @patch('src.connect.services.instagram.InstagramAPI')
    def test_connect_raises_error_if_user_social_auth_does_not_exist(self, mocked_instagram):
        api_object = Mock()
        follow = [Mock()]
        follow[0].outgoing_status = 'follows'
        api_object.follow_user.return_value = follow
        mocked_instagram.return_value = api_object

        self.other_social_auth.delete()

        connect = InstagramConnect(self.user)
        with pytest.raises(SocialUserNotFound):
            connection = connect.connect(self.other_user)
        api_object.follow_user.assert_not_called()


class YoutubeConnectTestCase(TestCase):
    def setUp(self):
        self.user_social_auth = mommy.make(
            'UserSocialAuth',
            provider='google-oauth2',
            extra_data={'access_token': '123456'}
        )
        self.user = self.user_social_auth.user

        self.other_social_auth = mommy.make(
            'UserSocialAuth',
            provider='google-oauth2',
            extra_data={'youtube_channel': 'UCTestYoutubeChannel'}
        )
        self.other_user = self.other_social_auth.user

    @patch.object(YoutubeConnect, '_authenticate')
    def test_initialization_calls_authenticate_for_user(self, authenticate):
        connect = YoutubeConnect(self.user)
        authenticate.assert_called_once_with(self.user)

    @patch('src.connect.services.youtube.googleapiclient')
    @patch('src.connect.services.youtube.google.oauth2.credentials')
    def test_authenticate_calls_api_with_tokens(self, mocked_credentials, mocked_google):
        connect = YoutubeConnect(self.user)
        mocked_credentials.Credentials.assert_called_once_with(
                token='123456',
                client_id=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
                client_secret=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
        )
        mocked_google.discovery.build.assert_called_once_with(
            'youtube', 'v3', credentials=mocked_credentials.Credentials.return_value
        )

    def test_authenticate_raises_error_if_no_user_social_auth(self):
        self.user_social_auth.delete()
        with pytest.raises(CredentialsNotFound):
            connect = YoutubeConnect(self.user)

    def test_authenticate_raises_error_if_no_user_credentials(self):
        self.user_social_auth.extra_data = {}
        self.user_social_auth.save()
        with pytest.raises(CredentialsNotFound):
            connect = YoutubeConnect(self.user)

    @patch('src.connect.services.youtube.googleapiclient')
    @patch('src.connect.services.youtube.google.oauth2.credentials')
    def test_connect_calls_create_subscription(self, mocked_credentials, mocked_client):
        api_object = Mock()
        mocked_client.discovery.build.return_value = api_object

        connect = YoutubeConnect(self.user)
        connection = connect.connect(self.other_user)
        assert connection is True
        api_object.subscriptions().insert.assert_called_once_with(
            body={'snippet': {
                'resourceId': {
                    'kind': 'youtube#channel',
                    'channelId': 'UCTestYoutubeChannel',
                }
            }}, part='snippet'
        )
        api_object.subscriptions().insert().execute.assert_called_once_with()

    @patch('src.connect.services.youtube.googleapiclient')
    @patch('src.connect.services.youtube.google.oauth2.credentials')
    def test_connect_raises_error_if_user_social_auth_does_not_exist(self, mocked_credentials, mocked_client):
        api_object = Mock()
        mocked_client.discovery.build.return_value = api_object

        self.other_social_auth.delete()

        connect = YoutubeConnect(self.user)
        with pytest.raises(SocialUserNotFound):
            connection = connect.connect(self.other_user)
        api_object.subscriptions().insert.assert_not_called()

    @patch('src.connect.services.youtube.googleapiclient')
    @patch('src.connect.services.youtube.google.oauth2.credentials')
    def test_connect_raises_error_if_other_user_dont_have_youtube_channel(self, mocked_credentials, mocked_client):
        api_object = Mock()
        mocked_client.discovery.build.return_value = api_object

        self.other_social_auth.extra_data = {}
        self.other_social_auth.save()

        connect = YoutubeConnect(self.user)
        with pytest.raises(SocialUserNotFound):
            connection = connect.connect(self.other_user)
        api_object.subscriptions().insert.assert_not_called()