from unittest.mock import Mock
from model_mommy import mommy

from django.contrib.auth import get_user_model
from django.test import TestCase

from src.core_auth.pipelines import profile_data

User = get_user_model()

class ProfileDataTestCase(TestCase):
    def setUp(self):
        self.user = mommy.make(User)
        self.response = {}
        self.details = {}
        self.backend = Mock()

    def test_profile_data_for_twitter_user(self):
        self.response['screen_name'] = 'test_user'
        self.response['profile_image_url'] = 'https://test.com/test_normal.png'
        self.backend.name = 'twitter'

        pipeline = profile_data(self.response, self.details, self.backend, self.user)

        assert pipeline is None

        self.user.refresh_from_db()

        assert self.user.picture == 'https://test.com/test.png'
        assert 'test_user' == self.user.social_profiles.get(provider='twitter').username

    def test_profile_data_for_facebook_user(self):
        self.response['name'] = 'test_user'
        self.response['id'] = '1'
        self.backend.name = 'facebook'

        pipeline = profile_data(self.response, self.details, self.backend, self.user)

        assert pipeline is None

        self.user.refresh_from_db()

        assert self.user.picture == 'https://graph.facebook.com/1/picture'
        assert 'test_user' == self.user.social_profiles.get(provider='facebook').username

    def test_profile_data_for_linkedin_user(self):
        self.details['fullname'] = 'test_user'
        self.backend.name = 'linkedin-oauth2'

        pipeline = profile_data(self.response, self.details, self.backend, self.user)

        assert pipeline is None

        self.user.refresh_from_db()

        assert self.user.picture is None
        assert 'test_user' == self.user.social_profiles.get(provider='linkedin-oauth2').username

    def test_profile_data_for_google_user(self):
        self.response['displayName'] = 'test_user'
        self.response['image'] = {'url': 'https://test.com/test.png'}
        self.backend.name = 'google-oauth2'

        pipeline = profile_data(self.response, self.details, self.backend, self.user)

        assert pipeline is None

        self.user.refresh_from_db()

        assert self.user.picture == 'https://test.com/test.png'
        assert 'test_user' == self.user.social_profiles.get(provider='google-oauth2').username

    def test_profile_data_for_instagram_user(self):
        self.response['user'] = {'username': 'test_user', 'profile_picture': 'https://test.com/test.png'}
        self.backend.name = 'instagram'

        pipeline = profile_data(self.response, self.details, self.backend, self.user)

        assert pipeline is None

        self.user.refresh_from_db()

        assert self.user.picture == 'https://test.com/test.png'
        assert 'test_user' == self.user.social_profiles.get(provider='instagram').username

    def test_do_not_update_user_picture(self):
        self.response['screen_name'] = 'test_user'
        self.response['profile_image_url_normal'] = 'https://test.com/test.png'
        self.backend.name = 'twitter'
        self.user.picture = 'http://test.com/picture.png'
        self.user.save()

        pipeline = profile_data(self.response, self.details, self.backend, self.user)

        assert pipeline is None

        self.user.refresh_from_db()

        assert self.user.picture == 'http://test.com/picture.png'
