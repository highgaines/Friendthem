from model_mommy import mommy
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from src.core_auth.serializers import UserSerializer

User = get_user_model()

class UserSerializerTests(APITestCase):
    def setUp(self):
        self.application = mommy.make(
            'Application', authorization_grant_type='password'
        )
        self.data = {
            'grant_type': 'password',
            'client_id': self.application.client_id,
            'client_secret': self.application.client_secret,
            'password': '123456',
            'username': 'test@example.com',
        }

    def test_create_user_for_valid_data(self):
        serializer = UserSerializer(data=self.data)
        assert serializer.is_valid()
        assert serializer.save() == User.objects.get(email='test@example.com')
        assert 'id' in serializer.data
        assert 'email' in serializer.data
        assert 'first_name' in serializer.data
        assert 'last_name' in serializer.data
        assert 'password' not in serializer.data

    def test_validate_application(self):
        self.data.update({'client_id': 'invalid_client_id'})
        serializer = UserSerializer(data=self.data)
        assert serializer.is_valid() is False
        assert 'non_field_errors' in serializer.errors

    def test_validate_username(self):
        mommy.make(User, email='test@example.com')
        serializer = UserSerializer(data=self.data)
        assert serializer.is_valid() is False
        assert 'username' in serializer.errors

    def test_retrieve_data_with_social_social_user(self):
        user = mommy.make(User, email='test@example.com')
        social_auth = mommy.make('UserSocialAuth', user=user, provider='snapchat')
        serializer = UserSerializer(user)
        assert 'id' in serializer.data
        assert 'email' in serializer.data
        assert 'first_name' in serializer.data
        assert 'last_name' in serializer.data
        assert 'password' not in serializer.data
        assert 'social_profiles' in serializer.data
        assert 1 == len(serializer.data['social_profiles'])

    def test_retrieve_data_with_social_profile_and_social_user(self):
        user = mommy.make(User, email='test@example.com')
        social_auth = mommy.make('UserSocialAuth', user=user, provider='snapchat')
        serializer = UserSerializer(user)
        assert 'id' in serializer.data
        assert 'email' in serializer.data
        assert 'first_name' in serializer.data
        assert 'last_name' in serializer.data
        assert 'password' not in serializer.data
        assert 'social_profiles' in serializer.data
        assert 1 == len(serializer.data['social_profiles'])
        assert social_auth.uid == serializer.data['social_profiles'][0]['uid']
