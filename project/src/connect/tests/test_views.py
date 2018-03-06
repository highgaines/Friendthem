from model_mommy import mommy
from rest_framework.test import APITestCase
from rest_framework.generics import CreateAPIView

from django.contrib.auth import get_user_model
from django.urls import reverse

from src.connect.views import ConnectionAPIView
from src.connect.serializers import ConnectionSerializer

User = get_user_model()


class ConnectionAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = mommy.make(User)
        self.client.force_authenticate(self.user)
        self.url = reverse('connect:connect')

    def test_login_required(self):
        self.client.logout()
        response = self.client.post(self.url)
        assert 401 == response.status_code

    def test_view_configuration(self):
        view_class = ConnectionAPIView
        view_class.serializer_class = ConnectionSerializer
        assert issubclass(view_class, CreateAPIView)


class ConnectedUsersAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = mommy.make(User)
        self.connected_user = mommy.make(User)
        mommy.make('SocialProfile', user=self.user, _quantity=4)
        mommy.make('SocialProfile', user=self.connected_user, _quantity=4)
        not_connected_user = mommy.make(User)
        mommy.make('Connection', user_1=self.user, user_2=self.connected_user, provider='youtube')
        mommy.make('Connection', user_1=self.user, user_2=self.connected_user, provider='twitter')
        self.client.force_authenticate(self.user)
        self.url = reverse('connect:users')

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        assert 401 == response.status_code

    def test_list_connected_users(self):
        response = self.client.get(self.url)
        assert 200 == response.status_code
        content = response.json()
        assert 1 == len(content)
        user_data = content[0]
        assert user_data['id'] == self.connected_user.id
        assert 50 == user_data['connection_percentage']

