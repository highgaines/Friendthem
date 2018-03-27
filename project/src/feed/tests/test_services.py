import pytest, responses
from unittest.mock import Mock, patch
from model_mommy import mommy

from twitter.models import Status

from django.conf import settings
from rest_framework.test import APITestCase

from src.feed.services import InstagramFeed, FacebookFeed, TwitterFeed
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

    @patch('src.feed.services.facebook')
    def test_get_image_and_likes(self, mocked_facebook):
        api = Mock()
        mocked_facebook.GraphAPI.return_value = api
        other_user = mommy.make(settings.AUTH_USER_MODEL)
        other_fb_user = mommy.make(
            'UserSocialAuth', user=other_user, uid='123', provider='facebook'
        )
        data =  [{
            "caption": "twitter.com",
            "description": "“https://t.co/ZO1ZwFpCXu”",
            "link": "https://example.com/link/",
            "name": "Test Name",
            "created_time": "2018-02-26T15:06:53+0000",
            "status_type": "shared_story",
            "message": "Test message",
            "id": "1774734319268445_1831679343543942",
            "attachments": {
                "data": [{
                    "description": "“https://t.co/ZO1ZwFpCXu”",
                    "media": {
                        "image": {
                            "height": 720,
                            "src": "https://example.com/test_src",
                            "width": 720
                        }
                    },
                    "target": {
                        "url": "https://example.com/test_url"
                    },
                    "title": "test title",
                    "type": "share",
                    "url": "https://example.com/facebook_url"
                }]
            }
        }, {
            "created_time": "2018-03-03T16:24:10+0000",
            "status_type": "mobile_status_update",
            "message": "Test test",
            "id": "1774734319238475_1837392089639334",
            "likes": {
                "data": [{
                    "id": "123",
                    "name": "Test User"
                }],
                "paging": {
                    "cursors": {
                        "before": "MTAyMTM5MDA4NjEwNjkzNzkZD",
                        "after": "MTAyMDQxOTc1OTAyNTc3NDMZD"
                    }
                },
                "summary": {
                    "total_count": 5,
                    "can_like": True,
                    "has_liked": False
                }
            }
        }]
        api.get_connections.return_value = {'data': data}
        feed = FacebookFeed(self.user)
        response = feed.get_feed(other_user)
        assert response[0]['img_url'] == 'https://example.com/test_src'
        assert response[0]['num_likes'] == 0
        assert response[0]['description'] == "Test Name"
        assert response[1]['img_url'] is None
        assert response[1]['num_likes'] == 5
        assert response[1]['description'] == 'Test test'

    def test_get_feed_raises_error_if_other_fb_user_does_not_exist(self):
        other_user = mommy.make(settings.AUTH_USER_MODEL)
        feed = FacebookFeed(self.user)
        with pytest.raises(SocialUserNotFound):
            feed.get_feed(other_user)


class TwitterFeedTestCase(APITestCase):
    def setUp(self):
        self.user = mommy.make(settings.AUTH_USER_MODEL)
        self.twitter_user = mommy.make(
            'UserSocialAuth', user=self.user, provider='twitter',
            extra_data={'access_token': {
                'oauth_token': 'abcde', 'oauth_token_secret': 'acdbe'
            }}
        )

    @patch('src.feed.services.twitter')
    def test_initialization_sets_api(self, mocked_twitter):
        api = Mock()
        mocked_twitter.Api.return_value = api
        feed = TwitterFeed(self.user)

        mocked_twitter.Api.assert_called_once_with(
            consumer_key=settings.SOCIAL_AUTH_TWITTER_KEY,
            consumer_secret=settings.SOCIAL_AUTH_TWITTER_SECRET,
            access_token_key='abcde', access_token_secret='acdbe'
        )

        assert feed.api == api

    def test_initialization_fails_if_social_user_does_not_exist(self):
        self.twitter_user.delete()
        with pytest.raises(CredentialsNotFound):
            feed = FacebookFeed(self.user)

    @patch('src.feed.services.TwitterFeed.format_data')
    @patch('src.feed.services.twitter')
    def test_get_feed_from_other_user(self, mocked_twitter, mocked_format):
        api = Mock()
        api.GetUserTimeline.return_value = [Status(), Status()]
        mocked_twitter.Api.return_value = api

        other_user = mommy.make(settings.AUTH_USER_MODEL)
        other_fb_user = mommy.make(
            'UserSocialAuth', user=other_user, uid='123', provider='twitter'
        )
        feed = TwitterFeed(self.user)
        feed.get_feed(other_user)

        assert 2 == mocked_format.call_count

    def test_get_feed_raises_error_if_other_fb_user_does_not_exist(self):
        other_user = mommy.make(settings.AUTH_USER_MODEL)
        feed = TwitterFeed(self.user)
        with pytest.raises(SocialUserNotFound):
            feed.get_feed(other_user)
