from unittest.mock import patch, Mock
from model_mommy import mommy
from django.conf import settings
from django.test import TestCase
from src.connect.pipelines import connect_existing_friends

class ConnectExistingFriendsTestCase(TestCase):
    def setUp(self):
        self.user = mommy.make(settings.AUTH_USER_MODEL)
        self.backend = Mock()

    @patch('src.connect.pipelines.services')
    def test_connect_existing_friends_calls_exisiting_connect_class(self, mocked_services):
        facebook_connect = Mock()
        facebook_connect.connect_users.return_value = []
        mocked_services.FacebookConnect.return_value = facebook_connect
        self.backend.name = 'facebook'

        connect_existing_friends(self.backend, self.user)

        mocked_services.FacebookConnect.assert_called_once_with(self.user)
        facebook_connect.connect_users.assert_called_once_with()

