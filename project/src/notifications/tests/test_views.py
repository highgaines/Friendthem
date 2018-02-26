from model_mommy import mommy
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model
from django.urls import reverse

from src.notifications.models import Device

User = get_user_model()

class ConnectionAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = mommy.make(User)
        self.client.force_authenticate(self.user)
        self.url = reverse('notifications:add_device')

    def test_login_required(self):
        self.client.logout()
        response = self.client.post(self.url)
        assert 401 == response.status_code

    def test_create_device_for_user(self):
        data = {'device_id': 'abcdef1234'}
        response = self.client.post(self.url, data=data)
        assert 201 == response.status_code
        device = Device.objects.first()
        assert 'abcdef1234' == device.device_id
        assert self.user == device.user

class NotificationsViewTestCase(APITestCase):
    def setUp(self):
        self.user = mommy.make(User)
        self.other_user = mommy.make(User)
        self.notification = mommy.make(
            'Notification', recipient=self.user, sender=self.other_user
        )
        self.client.force_authenticate(self.user)

        self.url = reverse('notifications:notifications')

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        assert 401 == response.status_code

    def test_list_notifications(self):
        response = self.client.get(self.url)
        assert 200 == response.status_code
        content = response.json()
        assert 1 == len(content)
        assert content[0]['message'] == self.notification.message
        assert content[0]['sender']['id'] == self.other_user.id
        assert content[0]['id'] == self.notification.id
