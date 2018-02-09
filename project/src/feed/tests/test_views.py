from unittest.mock import patch, Mock
from model_mommy import mommy

from django.conf import settings
from rest_framework.test import APITestCase

from django.urls import reverse

class FeedViewTestCase(APITestCase):
    def setUp(self):
        self.user = mommy.make(settings.AUTH_USER_MODEL)
        self.other_user = mommy.make(settings.AUTH_USER_MODEL)
        self.client.force_authenticate(self.user)
        self.url = reverse('feed:feed', kwargs={'user_id': self.other_user.id, 'provider': 'facebook'})

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)

        assert 401 == response.status_code

    @patch('src.feed.views.services')
    def test_get_data_from_facebook_service(self, mocked_services):
        facebook = Mock()
        facebook.get_feed.return_value = [
            {'a': 'b', 'created_time': 1},
            {'a': 'c', 'created_time': 2},
            {'d': 'e', 'created_time': 0}
        ]
        mocked_services.FacebookFeed.return_value = facebook

        response = self.client.get(self.url)
        assert 200 == response.status_code
        content = response.json()

        mocked_services.FacebookFeed.assert_called_with(self.user)
        facebook.get_feed.assert_called_with(self.other_user)

        assert (
            content['data'] == [
                {'a': 'c', 'created_time': 2},
                {'a': 'b', 'created_time': 1},
                {'d': 'e', 'created_time': 0}
            ]
        )

    def test_404_for_unexistent_user(self):
        self.other_user.delete()
        response = self.client.get(self.url)
        assert 404 == response.status_code

    def test_404_for_unexistent_provider(self):
        self.url = reverse('feed:feed', kwargs={'user_id': self.other_user.id, 'provider': 'invalid_provider'})
        response = self.client.get(self.url)
        assert 404 == response.status_code
