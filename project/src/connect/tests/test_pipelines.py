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

    @patch('src.connect.pipelines.services')
    def test_connect_existing_friends_calls_twitter_connect(self, mocked_services):
        twitter_connect = Mock()
        twitter_connect.connect_users.return_value = []
        mocked_services.TwitterConnect.return_value = twitter_connect
        self.backend.name = 'twitter-oauth2'

        connect_existing_friends(self.backend, self.user)

        mocked_services.TwitterConnect.assert_called_once_with(self.user)
        twitter_connect.connect_users.assert_called_once_with()

    @patch('src.connect.pipelines.services')
    def test_connect_existing_friends_calls_youtube_connect(self, mocked_services):
        youtube_connect = Mock()
        youtube_connect.connect_users.return_value = []
        mocked_services.YoutubeConnect.return_value = youtube_connect
        self.backend.name = 'google-oauth2'

        connect_existing_friends(self.backend, self.user)

        mocked_services.YoutubeConnect.assert_called_once_with(self.user)
        youtube_connect.connect_users.assert_called_once_with()

