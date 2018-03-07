from unittest.mock import patch, Mock
from model_mommy import mommy

from django.conf import settings
from django.urls import reverse
from rest_framework.test import APITestCase

from src.pictures.services import ProfilePicturesAlbumNotFound

class FacebookPicturesViewTestCase(APITestCase):
    def setUp(self):
        self.user = mommy.make(settings.AUTH_USER_MODEL)
        self.client.force_authenticate(self.user)
        self.url = reverse('pictures:facebook_pictures')

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)

        assert 401 == response.status_code

    @patch('src.pictures.views.FacebookProfilePicture')
    def test_get_pictures_from_facebook_service(self, mocked_service):
        service = Mock()
        mocked_service.return_value = service
        service.get_pictures.return_value = [
            {'id': 1, 'picture': 'https://example.com/picture1.png'},
            {'id': 2, 'picture': 'https://example.com/picture2.png'},
        ]
        response = self.client.get(self.url)
        assert 200 == response.status_code
        content = response.json()

        mocked_service.assert_called_with(self.user)
        service.get_pictures.assert_called_with()

        assert (
            content['data'] == [
                {'id': 1, 'picture': 'https://example.com/picture1.png'},
                {'id': 2, 'picture': 'https://example.com/picture2.png'},
            ]
        )

    @patch('src.pictures.views.FacebookProfilePicture')
    def test_return_error_if_service_raises(self, mocked_service):
        service = Mock()
        mocked_service.return_value = service
        service.get_pictures.side_effect = ProfilePicturesAlbumNotFound(
            'Could not find album with name equals to "Profile Pictures"'
        )

        response = self.client.get(self.url)
        assert 400 == response.status_code
        content = response.json()
        assert content['error'] == 'Could not find album with name equals to "Profile Pictures"'

        mocked_service.assert_called_with(self.user)
        service.get_pictures.assert_called_with()
