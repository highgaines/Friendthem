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
