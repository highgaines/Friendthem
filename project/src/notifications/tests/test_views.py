import uuid
from model_mommy import mommy
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model
from django.urls import reverse

from src.notifications.models import Device, Notification

User = get_user_model()

class DeviceAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = mommy.make(User)
        self.client.force_authenticate(self.user)
        self.url = reverse('notifications:add_device')

    def test_login_required(self):
        self.client.logout()
        response = self.client.post(self.url)
        assert 401 == response.status_code

    def test_create_device_for_user(self):
        device_id = uuid.uuid4()
        data = {'device_id': device_id}
        response = self.client.post(self.url, data=data)
        assert 201 == response.status_code
        device = Device.objects.first()
        assert device_id == device.device_id
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

class DeleteNotificationsViewTestCase(APITestCase):
    def setUp(self):
        self.user = mommy.make(User)
        self.other_user = mommy.make(User)
        self.notification = mommy.make(
            'Notification', recipient=self.user, sender=self.other_user
        )
        self.other_notification = mommy.make(
            'Notification', recipient=self.other_user,
        )
        self.client.force_authenticate(self.user)

        self.url = reverse(
            'notifications:delete_notification',
            kwargs={'pk': self.notification.id}
        )

    def test_login_required(self):
        self.client.logout()
        response = self.client.delete(self.url)
        assert 401 == response.status_code

    def test_post_not_allowed(self):
        response = self.client.post(self.url)
        assert 405 == response.status_code

    def test_get_not_allowed(self):
        response = self.client.get(self.url)
        assert 405 == response.status_code

    def test_delete_notification(self):
        response = self.client.delete(self.url)
        assert 204 == response.status_code
        assert Notification.objects.filter(id=self.notification.id).exists() is False

    def test_404_for_notification_for_other_user(self):
        url =  reverse(
            'notifications:delete_notification',
            kwargs={'pk': self.other_notification.id}
        )

        response = self.client.delete(url)
        assert 404 == response.status_code
        assert Notification.objects.filter(id=self.other_notification.id).exists() is True
