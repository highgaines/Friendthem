from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from model_mommy import mommy

from src.invite.models import Invite

User = get_user_model()

class ListCreateInviteViewTests(APITestCase):
    def setUp(self):
        self.user = mommy.make(User)
        self.client.force_authenticate(self.user)
        self.url = reverse('invite:invite')

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        assert 401 == response.status_code

    def test_create_invite(self):
        data = {'phone_number': '+553299999999'}
        response = self.client.post(self.url, data=data)
        assert 201 == response.status_code
        invite = Invite.objects.first()
        assert data['phone_number'] == invite.phone_number
        assert self.user == invite.user

    def test_cant_create_invite_with_same_user_and_phone_number(self):
        data = {'phone_number': '+553299999999'}
        Invite.objects.create(phone_number=data['phone_number'], user=self.user)
        response = self.client.post(self.url, data=data)
        assert 400 == response.status_code

    def test_list_invites(self):
        data = {'phone_number': '+553299999999'}
        Invite.objects.create(phone_number=data['phone_number'], user=self.user)
        response = self.client.get(self.url)
        assert 200 == response.status_code
        content = response.json()
        assert 1 == len(response.json())
        assert data == content[0]
