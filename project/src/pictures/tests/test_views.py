from unittest.mock import patch, Mock
from model_mommy import mommy

from django.conf import settings
from django.urls import reverse
from rest_framework.test import APITestCase

from src.pictures.models import UserPicture
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

class PictureDeleteUpdateView(APITestCase):
    def setUp(self):
        self.user = mommy.make(settings.AUTH_USER_MODEL)
        other_user = mommy.make(settings.AUTH_USER_MODEL)
        self.picture = mommy.make('UserPicture', user=self.user)
        self.other_picture = mommy.make('UserPicture', user=other_user)
        self.client.force_authenticate(self.user)
        self.url = reverse('pictures:pictures_delete_update', kwargs={'pk': self.picture.id})

    def test_login_required(self):
        self.client.logout()
        response = self.client.delete(self.url)

        assert 401 == response.status_code

    def test_delete_picture(self):
        response = self.client.delete(self.url)
        assert 200 == response.status_code
        assert UserPicture.objects.filter(id=self.picture.id).exists() is False
        assert UserPicture.objects.filter(id=self.other_picture.id).exists() is True
        assert response.json() == []

    def test_update_picture(self):
        data = {'url': 'http://example.com/example.jpg'}
        response = self.client.put(self.url, data)
        assert 200 == response.status_code
        self.picture.refresh_from_db()
        assert 'http://example.com/example.jpg' == self.picture.url
        assert response.json() == [{'id': 27, 'url': 'http://example.com/example.jpg'}]

    def test_update_400_for_invalid_url(self):
        data = {'url': 'invalid_url'}
        response = self.client.put(self.url, data)
        assert 400 == response.status_code

    def test_404_for_picture_for_other_user(self):
        self.url = reverse('pictures:pictures_delete_update', kwargs={'pk': self.other_picture.id})
        response = self.client.update(self.url)
        assert 404 == response.status_code

    def test_404_for_picture_for_other_user(self):
        self.url = reverse('pictures:pictures_delete_update', kwargs={'pk': self.other_picture.id})
        response = self.client.delete(self.url)
        assert 404 == response.status_code
        assert UserPicture.objects.filter(id=self.picture.id).exists() is True
        assert UserPicture.objects.filter(id=self.other_picture.id).exists() is True

class PictureListCreateView(APITestCase):
    def setUp(self):
        self.user = mommy.make(settings.AUTH_USER_MODEL)
        other_user = mommy.make(settings.AUTH_USER_MODEL)
        self.picture = mommy.make('UserPicture', user=self.user)
        self.other_picture = mommy.make('UserPicture', user=other_user)
        self.client.force_authenticate(self.user)
        self.url = reverse('pictures:pictures')

    def test_login_required_for_create(self):
        self.client.logout()
        response = self.client.post(self.url)

        assert 401 == response.status_code

    def test_login_required_for_list(self):
        self.client.logout()
        response = self.client.get(self.url)

        assert 401 == response.status_code

    def test_list_pictures(self):
        response = self.client.get(self.url)
        assert 200 == response.status_code
        content = response.json()
        assert 1 == len(content)
        assert content == [{'id': self.picture.id, 'url': self.picture.url}]
        assert self.picture.url == content[0]['url']
        assert self.picture.id == content[0]['id']

    def test_post_creates_picture_for_user(self):
        data = {'url': 'http://example.com/test.jpg'}
        response = self.client.post(self.url, data)
        assert 201 == response.status_code
        assert 2 == UserPicture.objects.filter(user=self.user).count()
        content = response.json()
        assert 2 == len(content)
