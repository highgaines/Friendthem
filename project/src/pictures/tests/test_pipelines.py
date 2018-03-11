from unittest.mock import Mock, patch
from model_mommy import mommy

from django.conf import settings
from django.test import TestCase

from src.pictures.models import UserPicture
from src.pictures.pipelines import autoset_user_pictures
from src.pictures.exceptions import ProfilePicturesAlbumNotFound

class AutosetUserPicturesTestCase(TestCase):
    @patch('src.pictures.pipelines.FacebookProfilePicture')
    def test_autoset_user_picture_for_6_pictures(self, mocked_service_cls):
        service = Mock()
        service.get_pictures.return_value = [
            {'id': 1, 'picture': 'http://example.com/1.jpg'},
            {'id': 2, 'picture': 'http://example.com/2.jpg'},
            {'id': 3, 'picture': 'http://example.com/3.jpg'},
            {'id': 4, 'picture': 'http://example.com/4.jpg'},
            {'id': 5, 'picture': 'http://example.com/5.jpg'},
            {'id': 6, 'picture': 'http://example.com/5.jpg'},
        ]
        mocked_service_cls.return_value = service
        user = mommy.make(settings.AUTH_USER_MODEL)
        backend = Mock()
        backend.name = 'facebook'

        response = autoset_user_pictures(backend, user)
        assert 6 == len(response['pictures'])
        assert 6 == user.pictures.count()

    @patch('src.pictures.pipelines.FacebookProfilePicture')
    def test_autoset_user_picture_for_5_pictures(self, mocked_service_cls):
        service = Mock()
        service.get_pictures.return_value = [
            {'id': 1, 'picture': 'http://example.com/1.jpg'},
            {'id': 2, 'picture': 'http://example.com/2.jpg'},
            {'id': 3, 'picture': 'http://example.com/3.jpg'},
            {'id': 4, 'picture': 'http://example.com/4.jpg'},
            {'id': 5, 'picture': 'http://example.com/5.jpg'},
        ]
        mocked_service_cls.return_value = service
        user = mommy.make(settings.AUTH_USER_MODEL)
        backend = Mock()
        backend.name = 'facebook'

        response = autoset_user_pictures(backend, user)
        assert 5 == len(response['pictures'])
        assert 5 == user.pictures.count()

    @patch('src.pictures.pipelines.FacebookProfilePicture')
    def test_autoset_user_picture_for_7_pictures(self, mocked_service_cls):
        service = Mock()
        service.get_pictures.return_value = [
            {'id': 1, 'picture': 'http://example.com/1.jpg'},
            {'id': 2, 'picture': 'http://example.com/2.jpg'},
            {'id': 3, 'picture': 'http://example.com/3.jpg'},
            {'id': 4, 'picture': 'http://example.com/4.jpg'},
            {'id': 5, 'picture': 'http://example.com/5.jpg'},
            {'id': 6, 'picture': 'http://example.com/5.jpg'},
            {'id': 7, 'picture': 'http://example.com/7.jpg'},
        ]
        mocked_service_cls.return_value = service
        user = mommy.make(settings.AUTH_USER_MODEL)
        backend = Mock()
        backend.name = 'facebook'

        response = autoset_user_pictures(backend, user)
        assert 6 == len(response['pictures'])
        assert 6 == user.pictures.count()

    @patch('src.pictures.pipelines.FacebookProfilePicture')
    def test_dont_set_user_picture_if_user_has_picture(self, mocked_service_cls):
        service = Mock()
        mocked_service_cls.return_value = service
        user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('UserPicture', user=user)
        backend = Mock()
        backend.name = 'facebook'

        response = autoset_user_pictures(backend, user)
        mocked_service_cls.assert_not_called()
        service.get_pictures.assert_not_called()
        assert 1 == user.pictures.count()

    @patch('src.pictures.pipelines.FacebookProfilePicture')
    def test_dont_set_user_picture_if_other_backend(self, mocked_service_cls):
        service = Mock()
        mocked_service_cls.return_value = service
        user = mommy.make(settings.AUTH_USER_MODEL)
        backend = Mock()
        backend.name = 'twitter'

        response = autoset_user_pictures(backend, user)
        mocked_service_cls.assert_not_called()
        service.get_pictures.assert_not_called()
        assert 0 == user.pictures.count()

    @patch('src.pictures.pipelines.FacebookProfilePicture')
    def test_dont_set_user_picture_if_profile_album_not_found(self, mocked_service_cls):
        service = Mock()
        mocked_service_cls.return_value = service
        service.get_pictures.side_effect = ProfilePicturesAlbumNotFound
        user = mommy.make(settings.AUTH_USER_MODEL)
        backend = Mock()
        backend.name = 'facebook'

        response = autoset_user_pictures(backend, user)
        mocked_service_cls.assert_called_once_with(user)
        service.get_pictures.assert_called_once_with()
        assert 0 == user.pictures.count()
