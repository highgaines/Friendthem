from unittest.mock import Mock, patch
import pytest
from model_mommy import mommy
from django.conf import settings
from rest_framework.test import APITestCase
from src.pictures.services import FacebookProfilePicture
from src.connect.exceptions import CredentialsNotFound

class FacebookProfilePictureTestCase(APITestCase):
    def setUp(self):
        self.user = mommy.make(settings.AUTH_USER_MODEL)
        self.facebook_user = mommy.make(
            'UserSocialAuth', user=self.user, provider='facebook', extra_data={
                'access_token': 'fb_access_token'
            }
        )

    @patch('src.pictures.services.facebook')
    def test_initialization_sets_api(self, mocked_facebook):
        api = Mock()
        mocked_facebook.GraphAPI.return_value = api
        feed = FacebookProfilePicture(self.user)

        assert mocked_facebook.GraphAPI.called_once_with('fb_access_token')
        assert feed.api == api


    def test_initialization_fails_if_social_user_does_not_exist(self):
        self.facebook_user.delete()
        with pytest.raises(CredentialsNotFound):
            feed = FacebookProfilePicture(self.user)

    @patch.object(FacebookProfilePicture, 'get_profile_picture_album')
    @patch('src.pictures.services.facebook')
    def test_get_pictures(self, mocked_facebook, mocked_get_album):
        mocked_get_album.return_value = {'id': 23}
        api = Mock()
        api.get_connections.return_value = {'data': [
            {'id': 1, 'images': [
                {'height': 600, 'source': 'https://example.com/x600.jpg?query=query'},
                {'height': 300, 'source': 'https://example.com/x300.jpg?query=query'},
                {'height': 800, 'source': 'https://example.com/x800.jpg?query=query'},
            ]}
        ]}
        mocked_facebook.GraphAPI.return_value = api

        feed = FacebookProfilePicture(self.user)
        response = feed.get_pictures()

        api.get_connections.assert_called_once_with(23, 'photos', fields='images', limit=200)

        assert [{'id': 1, 'picture': 'https://example.com/x800.jpg?query=query'}] == response
