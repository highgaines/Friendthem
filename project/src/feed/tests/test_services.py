import pytest, responses
from unittest.mock import Mock, patch
from model_mommy import mommy

from django.conf import settings
from rest_framework.test import APITestCase

from src.feed.services import InstagramFeed, FacebookFeed
from src.connect.exceptions import CredentialsNotFound, SocialUserNotFound

class InstagramFeedTestCase(APITestCase):
    def setUp(self):
        self.user = mommy.make(settings.AUTH_USER_MODEL)
        self.instagram_user = mommy.make(
            'UserSocialAuth', user=self.user, provider='instagram', extra_data={
                'access_token': 'insta_access_token'
            }
        )

    def test_initialization_sets_access_token(self):
        feed = InstagramFeed(self.user)

        assert feed.access_token == 'insta_access_token'

    def test_initialization_fails_if_social_user_does_not_exist(self):
        self.instagram_user.delete()
        with pytest.raises(CredentialsNotFound):
            feed = InstagramFeed(self.user)

    @responses.activate
    @patch('src.feed.services.InstagramFeed.format_data')
    def test_get_feed_from_other_user(self, mocked_format):
        other_user = mommy.make(settings.AUTH_USER_MODEL)
        other_insta_user = mommy.make(
            'UserSocialAuth', user=other_user, uid='123', provider='instagram'
        )
        responses.add(
            responses.GET,
            'https://api.instagram.com/v1/users/123/media/recent'
            '?access_token=insta_access_token', json={'data': ['mocked_data_1', 'mocked_data_2']}
        )
        feed = InstagramFeed(self.user)
        feed.get_feed(other_user)

        assert 2 == mocked_format.call_count

    def test_get_feed_raises_error_if_other_insta_user_does_not_exist(self):
        other_user = mommy.make(settings.AUTH_USER_MODEL)
        feed = InstagramFeed(self.user)
        with pytest.raises(SocialUserNotFound):
            feed.get_feed(other_user)

class FacebookFeedTestCase(APITestCase):
    def setUp(self):
        self.user = mommy.make(settings.AUTH_USER_MODEL)
        self.facebook_user = mommy.make(
            'UserSocialAuth', user=self.user, provider='facebook', extra_data={
                'access_token': 'fb_access_token'
            }
        )

    @patch('src.feed.services.facebook')
    def test_initialization_sets_api(self, mocked_facebook):
        api = Mock()
        mocked_facebook.GraphAPI.return_value = api
        feed = FacebookFeed(self.user)

        assert mocked_facebook.GraphAPI.called_once_with('fb_access_token')
        assert feed.api == api

    def test_initialization_fails_if_social_user_does_not_exist(self):
        self.facebook_user.delete()
        with pytest.raises(CredentialsNotFound):
            feed = FacebookFeed(self.user)

    @patch('src.feed.services.FacebookFeed.format_data')
    @patch('src.feed.services.facebook')
    def test_get_feed_from_other_user(self, mocked_facebook, mocked_format):
        api = Mock()
        api.get_connections.return_value = {'data': ['mocked_data_1', 'mocked_data_2']}
        mocked_facebook.GraphAPI.return_value = api

        other_user = mommy.make(settings.AUTH_USER_MODEL)
        other_fb_user = mommy.make(
            'UserSocialAuth', user=other_user, uid='123', provider='facebook'
        )
        feed = FacebookFeed(self.user)
        feed.get_feed(other_user)

        assert 2 == mocked_format.call_count

    def test_get_feed_raises_error_if_other_fb_user_does_not_exist(self):
        other_user = mommy.make(settings.AUTH_USER_MODEL)
        feed = FacebookFeed(self.user)
        with pytest.raises(SocialUserNotFound):
            feed.get_feed(other_user)
