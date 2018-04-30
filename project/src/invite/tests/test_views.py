from django.contrib.auth import get_user_model
from django.urls import reverse
from model_mommy import mommy

from src.invite.models import Invite

User = get_user_model()

    def setUp(self):
        self.user = mommy.make(User)

        response = self.client.get(self.url)
        assert 200 == response.status_code
