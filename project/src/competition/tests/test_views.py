from django.urls import reverse

from model_mommy import mommy
from rest_framework.test import APITestCase
from src.competition.models import CompetitionUser


class CompetitionUserRetrieveViewForAuthUser(APITestCase):
    def setUp(self):
        self.user = mommy.make(CompetitionUser)
        self.client.force_authenticate(self.user)
        self.url = reverse('competition:competition_auth_user')

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        assert 401 == response.status_code

    def test_retrieve_total_points_for_authed_user(self):
        response = self.client.get(self.url)
        assert 200 == response.status_code
        assert 'total_points'in response.json()


class CompetitionUserRetrieveViewForOtherUser(APITestCase):
    def setUp(self):
        self.user = mommy.make(CompetitionUser)
        self.other_user = mommy.make(CompetitionUser)
        self.client.force_authenticate(self.user)
        self.url = reverse('competition:competition_user', kwargs={'user_id': self.other_user.id})

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        assert 401 == response.status_code

    def test_retrieve_total_points_for_other_user(self):
        response = self.client.get(self.url)
        assert 200 == response.status_code
        assert 'total_points'in response.json()

    def test_return_400_if_unexistent_id(self):
        self.url = reverse(
            'competition:competition_user', kwargs={'user_id': 999}
        )
        response = self.client.get(self.url)
        assert 404 == response.status_code
