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

