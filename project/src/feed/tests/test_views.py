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
        self.url = reverse('feed:feed', kwargs={'user_id': self.other_user.id})

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)

        assert 401 == response.status_code

    @patch('src.feed.views.FacebookFeed')
    @patch('src.feed.views.InstagramFeed')
    def test_get_data_from_services(self, mocked_instagram, mocked_facebook):
        instagram = Mock()
        instagram.get_feed.return_value = [{'a': 'b', 'created_time': 1}, {'d': 'e', 'created_time': 0}]
        mocked_instagram.return_value = instagram

        facebook = Mock()
        facebook.get_feed.return_value = [{'a': 'c', 'created_time': 2}]
        mocked_facebook.return_value = facebook

        response = self.client.get(self.url)
        assert 200 == response.status_code
        content = response.json()

        assert (
            content['data'] == [
                {'a': 'c', 'created_time': 2},
                {'a': 'b', 'created_time': 1},
                {'d': 'e', 'created_time': 0}
            ]
        )
