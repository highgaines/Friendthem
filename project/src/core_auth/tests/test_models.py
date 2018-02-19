import pytest
from model_mommy import mommy

from django.test import TestCase
from src.core_auth.models import User

class TestUserManager(TestCase):
    def test_raise_error_if_email_in_empty(self):
        with pytest.raises(ValueError):
            User.objects.create_user('')

    def test_create_user_with_email(self):
        user = User.objects.create_user('test@example.com', 'TesT!45D2')
        assert user.is_superuser is False
        assert user.is_staff is False

    def test_create_superuser(self):
        user = User.objects.create_superuser('test@example.com', 'TesT!45D2')
        assert user.is_superuser is True
        assert user.is_staff is True

    def test_raise_error_if_email_in_empty_for_superuser(self):
        with pytest.raises(ValueError):
            User.objects.create_superuser('', 'TesT!45D2')

class TestSocialProfile(TestCase):
    def test_social_profile_str(self):
        profile = mommy.make('SocialProfile')
        assert str(profile) == profile.user.email
