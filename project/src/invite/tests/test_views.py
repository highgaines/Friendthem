import uuid
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from model_mommy import mommy

from src.invite.models import Invite

User = get_user_model()

class CheckInviteTestCase(TestCase):
    def setUp(self):
        self.user = mommy.make(User)
        self.uuid = uuid.uuid4()
        self.url = reverse('invite:check_invite', kwargs={'user_id': self.user.id})

    def test_get_returns_correct_template(self):
        response = self.client.get(self.url)
        assert 200 == response.status_code
        assert 'check_invite.html' == response.templates[0].name

    def test_get_returns_404_if_user_does_not_exist(self):
        self.url = reverse('invite:check_invite', kwargs={'user_id': 999})
        response = self.client.get(self.url)
        assert 404 == response.status_code

    def test_post_creates_invite_if_device_and_invite_dont_exist(self):
        response = self.client.post(self.url, data={'device-id': self.uuid})
        assert 302 == response.status_code
        assert response['Location'] == settings.STORE_URL
        assert 1 == Invite.objects.count()

    def test_post_doesnt_create_invite_if_device_exists(self):
        mommy.make('Device', device_id=self.uuid)
        response = self.client.post(self.url, data={'device-id': self.uuid})
        assert 302 == response.status_code
        assert response['Location'] == settings.STORE_URL
        assert 0 == Invite.objects.count()

    def test_post_doesnt_create_invite_if_invite_alredy_exists(self):
        mommy.make('Invite', user=self.user, device_id=self.uuid)
        response = self.client.post(self.url, data={'device-id': self.uuid})
        assert 302 == response.status_code
        assert response['Location'] == settings.STORE_URL
        assert 1 == Invite.objects.count()

    def test_post_returns_404_if_user_does_not_exist(self):
        self.url = reverse('invite:check_invite', kwargs={'user_id': 999})
        response = self.client.post(self.url)
        assert 404 == response.status_code
