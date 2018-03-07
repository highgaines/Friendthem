from unittest.mock import patch, Mock
from model_mommy import mommy

from django.conf import settings
from django.urls import reverse
from rest_framework.test import APITestCase

from src.pictures.models import UserPicture
from src.pictures.services import ProfilePicturesAlbumNotFound

class FeedViewTestCase(APITestCase):
    def setUp(self):
        self.user = mommy.make(settings.AUTH_USER_MODEL)
        self.client.force_authenticate(self.user)
        self.url = reverse('pictures:pictures')

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

class PictureDeleteView(APITestCase):
    def setUp(self):
        self.user = mommy.make(settings.AUTH_USER_MODEL)
        other_user = mommy.make(settings.AUTH_USER_MODEL)
        self.picture = mommy.make('UserPicture', user=self.user)
        self.other_picture = mommy.make('UserPicture', user=other_user)
        self.client.force_authenticate(self.user)
        self.url = reverse('pictures:pictures_delete', kwargs={'pk': self.picture.id})

    def test_login_required(self):
        self.client.logout()
        response = self.client.delete(self.url)

        assert 401 == response.status_code

    def test_delete_picture(self):
        response = self.client.delete(self.url)
        assert 204 == response.status_code
        assert UserPicture.objects.filter(id=self.picture.id).exists() is False
        assert UserPicture.objects.filter(id=self.other_picture.id).exists() is True

    def test_404_for_picture_for_other_user(self):
        self.url = reverse('pictures:pictures_delete', kwargs={'pk': self.other_picture.id})
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

    def test_list_picture(self):
        response = self.client.get(self.url)
        assert 200 == response.status_code
        content = response.json()
        assert 1 == len(content)
        assert self.picture.url == content[0]['url']
        assert self.picture.id == content[0]['id']

    def test_post_creates_picture_for_user(self):
        data = {'url': 'http://example.com/test.jpg'}
        response = self.client.post(self.url, data)
        assert 201 == response.status_code
        assert 2 == UserPicture.objects.filter(user=self.user).count()

    def test_validation_error_for_user_with_6_pictures(self):
        mommy.make('UserPicture', user=self.user, _quantity=5)
        data = {'url': 'http://example.com/test.jpg'}
        response = self.client.post(self.url, data)
        assert 400 == response.status_code
        assert response.json() == {
            'non_field_errors': ['User already has 6 pictures. You must delete one before adding other.']
        }
        assert 6 == UserPicture.objects.filter(user=self.user).count()
