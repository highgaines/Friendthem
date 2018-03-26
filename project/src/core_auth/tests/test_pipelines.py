import pytest
from unittest.mock import Mock, patch
from model_mommy import mommy

from django.contrib.auth import get_user_model
from django.test import TestCase
from social_django.models import UserSocialAuth

from src.core_auth.pipelines import profile_data, get_user, create_user, get_youtube_channel
from src.core_auth.exceptions import YoutubeChannelNotFound

User = get_user_model()

class GetUserTestCase(TestCase):
    def test_get_user_from_strategy_if_not_in_kwargs(self):
        user = mommy.make(User)
        strategy = Mock()
        strategy.request.user = user
        response = get_user(strategy)

        assert response['user'] == user

    def test_get_user_from_kwargs(self):
        user = mommy.make(User)
        strategy = Mock()
        response = get_user(strategy, user=user)

        assert response['user'] == user

    def test_get_user_gets_user_from_kwargs_if_in_kwargs_and_strategy(self):
        user = mommy.make(User)
        other_user = mommy.make(User)
        strategy = Mock()
        strategy.request.user = other_user
        response = get_user(strategy, user=user)

        assert response['user'] == user

    def test_return_none_if_anonymous_user(self):
        strategy = Mock()
        strategy.request.user.is_anonymous = True
        response = get_user(strategy)

        assert response is None

class CreateUserTestCase(TestCase):
    def test_create_user_with_email(self):
        backend = Mock()
        backend.setting.return_value = ['email']
        strategy = Mock()
        details = Mock()
        kwargs = {'email': 'test@example.com'}
        create_user(strategy, details, backend, **kwargs)

        strategy.create_user.assert_called_once_with(**kwargs)

    @patch('src.core_auth.pipelines.random')
    @patch('src.core_auth.pipelines.string')
    def test_create_user_with_random_email_for_facebook(self, string, random):
        backend = Mock()
        backend.name = 'facebook'
        backend.setting.return_value = ['email']
        strategy = Mock()
        details = {}
        kwargs = {'email': ''}
        create_user(strategy, details, backend, **kwargs)

        random.choices.assert_called_once_with(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=32)

        assert 1 == strategy.create_user.call_count


class ProfileDataTestCase(TestCase):
    def setUp(self):
        self.user = mommy.make(User)
        self.social = mommy.make('UserSocialAuth')
        self.response = {}
        self.details = {}
        self.backend = Mock()

    def test_profile_data_for_twitter_user(self):
        self.response['screen_name'] = 'test_user'
        self.response['profile_image_url'] = 'https://test.com/test_normal.png'
        self.backend.name = 'twitter'

        pipeline = profile_data(
            self.response, self.details, self.backend, self.user, self.social)

        assert pipeline is None

        self.user.refresh_from_db()

        assert self.user.picture == 'https://test.com/test.png'
        assert 'test_user' == self.social.extra_data.get('username')

    def test_profile_data_for_facebook_user(self):
        self.response['name'] = 'test_user'
        self.response['id'] = '1'
        self.backend.name = 'facebook'

        pipeline = profile_data(
            self.response, self.details, self.backend, self.user, self.social
        )

        assert pipeline is None

        self.user.refresh_from_db()
        self.social.refresh_from_db()

        assert self.user.picture == 'https://graph.facebook.com/1/picture?type=large'
        assert 'test_user' == self.social.extra_data.get('username')

    def test_complete_profile_data_for_facebook_user(self):
        self.response = {
            'name': 'Test User',
            'id': '1',
            'hometown': {'id': 45, 'name': 'Boring, OR'},
            'about': 'Test Boring About Coming Soon!',
            'age_range': {
                'min': 18, 'max': 39,
            },
            'work': [
                {
                    'employer': {'id': 2, 'name': 'Test Employer'},
                    'start_date': '2018-01-01',
                    'position': {'id': 4, 'name': 'Test Occupation'},
                },
                {
                    'employer': {'id': 2, 'name': 'Test Old Employer'},
                    'start_date': '2017-01-01',
                    'position': {'id': 4, 'name': 'Test Old Occupation'},
                },
                {
                    'employer': {'id': 2, 'name': 'Test None Employer'},
                    'position': {'id': 4, 'name': 'Test None Occupation'},
                },
            ]
        }
        self.backend.name = 'facebook'

        pipeline = profile_data(
            self.response, self.details, self.backend, self.user, self.social
        )

        assert pipeline is None

        self.user.refresh_from_db()

        assert self.user.hometown == 'Boring, OR'
        assert self.user.bio == 'Test Boring About Coming Soon!'
        assert self.user.age_range == '18 - 39'
        assert self.user.employer == 'Test Employer'
        assert self.user.occupation == 'Test Occupation'
        assert self.user.picture == 'https://graph.facebook.com/1/picture?type=large'
        assert 'Test User' == self.social.extra_data.get('username')

    def test_profile_data_for_linkedin_user(self):
        self.details['fullname'] = 'test_user'
        self.backend.name = 'linkedin-oauth2'

        pipeline = profile_data(
            self.response, self.details, self.backend, self.user, self.social
        )

        assert pipeline is None

        self.user.refresh_from_db()

        assert self.user.picture is None
        assert 'test_user' == self.social.extra_data['username']

    def test_profile_data_for_google_user(self):
        self.response['displayName'] = 'test_user'
        self.response['image'] = {'url': 'https://test.com/test.png'}
        self.backend.name = 'google-oauth2'

        pipeline = profile_data(
            self.response, self.details, self.backend, self.user, self.social
        )

        assert pipeline is None

        self.user.refresh_from_db()

        assert self.user.picture == 'https://test.com/test.png'
        assert 'test_user' == self.social.extra_data.get('username')

    def test_profile_data_for_instagram_user(self):
        self.response['user'] = {'username': 'test_user', 'profile_picture': 'https://test.com/test.png'}
        self.backend.name = 'instagram'

        pipeline = profile_data(
            self.response, self.details, self.backend, self.user, self.social
        )

        assert pipeline is None

        self.user.refresh_from_db()
        self.social.refresh_from_db()

        assert self.user.picture == 'https://test.com/test.png'
        assert 'test_user' == self.social.extra_data.get('username')

    def test_do_not_update_user_picture(self):
        self.response['screen_name'] = 'test_user'
        self.response['profile_image_url_normal'] = 'https://test.com/test.png'
        self.backend.name = 'twitter'
        self.user.picture = 'http://test.com/picture.png'
        self.user.save()

        pipeline = profile_data(
            self.response, self.details, self.backend, self.user, self.social
        )

        assert pipeline is None

        self.user.refresh_from_db()

        assert self.user.picture == 'http://test.com/picture.png'


class GetYoutubeChannelTestCase(TestCase):
    def setUp(self):
        self.backend = Mock()
        self.strategy = Mock()
        self.backend.name = 'google-oauth2'
        self.social = mommy.make(UserSocialAuth)

    @patch('src.core_auth.pipelines.googleapiclient')
    @patch('src.core_auth.pipelines.google.oauth2.credentials')
    @patch.object(UserSocialAuth, 'get_access_token')
    def test_get_youtube_channel_if_it_is_public(self, refresh_token, mocked_credentials, mocked_client):
        api_object = Mock()
        list_action = Mock()
        mocked_client.discovery.build.return_value = api_object
        list_action.execute.return_value = {
            'kind': 'youtube#channelListResponse',
            'etag': 'hshsahskdasd',
            'pageInfo': {'totalResults': 1, 'resultsPerPage': 1},
            'items': [
                {
                    'kind': 'youtube#channel',
                    'etag': 'djaosidjaoisdj',
                    'id': 'UCYoutubeChannel',
                    'status': {
                        'privacyStatus': 'public', 'isLinked': True, 'longUploadsStatus': 'allowed'
                    }
                }
            ]
        }

        api_object.channels().list.return_value = list_action

        get_youtube_channel(self.strategy, self.backend, self.social)

        api_object.channels().list.assert_called_once_with(
            mine=True, part='id,status'
        )

        self.social.refresh_from_db()
        assert self.social.extra_data['youtube_channel'] == 'UCYoutubeChannel'

    @patch('src.core_auth.pipelines.googleapiclient')
    @patch('src.core_auth.pipelines.google.oauth2.credentials')
    @patch.object(UserSocialAuth, 'get_access_token')
    def test_get_youtube_channel_raises_errors_if_not_public(self, refresh_token, mocked_credentials, mocked_client):
        api_object = Mock()
        list_action = Mock()
        mocked_client.discovery.build.return_value = api_object
        list_action.execute.return_value = {
            'kind': 'youtube#channelListResponse',
            'etag': 'hshsahskdasd',
            'pageInfo': {'totalResults': 1, 'resultsPerPage': 1},
            'items': [
                {
                    'kind': 'youtube#channel',
                    'etag': 'djaosidjaoisdj',
                    'id': 'UCYoutubeChannel',
                    'status': {
                        'privacyStatus': 'private', 'isLinked': True, 'longUploadsStatus': 'allowed'
                    }
                }
            ]
        }

        api_object.channels().list.return_value = list_action
        with pytest.raises(YoutubeChannelNotFound):
            get_youtube_channel(self.strategy, self.backend, self.social)

            api_object.channels().list.assert_called_once_with(
                mine=True, part='id,status'
            )

        assert 0 == UserSocialAuth.objects.count()
