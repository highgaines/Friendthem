from model_mommy import mommy
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from oauth2_provider.models import AccessToken

User = get_user_model()

class RegisterUserViewTests(APITestCase):

    def setUp(self):
        self.application = mommy.make('Application', authorization_grant_type='password')
        self.url = reverse('auth:register')

    def test_register_user_with_correct_data(self):
        data = {
            'client_id': self.application.client_id,
            'client_secret': self.application.client_secret,
            'grant_type': 'password',
            'username': 'xpto@example.com',
            'password': '123456',
        }
        response = self.client.post(self.url, data)
        content = response.json()

        assert 200 == response.status_code
        assert 'access_token' in content
        assert 'expires_in' in content
        assert 'scope' in content
        assert 'refresh_token' in content
        assert 'Bearer' == content['token_type']

        assert 1 == User.objects.count()
        user = User.objects.first()
        access_token = AccessToken.objects.get(token=content['access_token'])
        assert user == access_token.user

    def test_raises_400_if_invalid_application(self):
        data = {
            'client_id': 'invalid id',
            'client_secret': 'invalid secret',
            'grant_type': 'invalid grant',
            'username': 'xpto@example.com',
            'password': '123456',
        }
        response = self.client.post(self.url, data)
        content = response.json()

        assert 400 == response.status_code
        assert 0 == User.objects.count()

    def test_raises_400_if_user_already_exists(self):
        mommy.make(User, email='xpto@example.com')
        data = {
            'client_id': 'invalid id',
            'client_secret': 'invalid secret',
            'grant_type': 'invalid grant',
            'username': 'xpto@example.com',
            'password': '123456',
        }
        response = self.client.post(self.url, data)
        content = response.json()

        assert 400 == response.status_code
        assert 1 == User.objects.count()


class UserDetailViewTests(APITestCase):
    def setUp(self):
        self.user = mommy.make(User)
        self.client.force_authenticate(self.user)
        self.url = reverse('auth:me')

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        assert 401 == response.status_code

    def test_returns_correct_data_for_user(self):
        response = self.client.get(self.url)
        assert 200 == response.status_code

        content = response.json()
        assert self.user.email == content['email']
        assert self.user.id == content['id']

