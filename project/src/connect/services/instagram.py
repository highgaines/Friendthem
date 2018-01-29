from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from instagram import InstagramAPI
from src.connect.services.base import BaseConnect
from src.connect.exceptions import CredentialsNotFound, SocialUserNotFound

class InstagramConnect(BaseConnect):
    def _authenticate(self, user):
        try:
            social_auth = user.social_auth.get(provider='instagram')
            token_key = social_auth.extra_data['access_token']
        except (ObjectDoesNotExist, KeyError):
            raise CredentialsNotFound

        return InstagramAPI(
            client_secret=settings.SOCIAL_AUTH_INSTAGRAM_SECRET,
            access_token=token_key
        )

    def connect(self, other_user):
        try:
            other_social_auth = other_user.social_auth.get(provider='instagram')
            other_user_id = other_social_auth.uid
        except ObjectDoesNotExist:
            raise SocialUserNotFound

        follow = self.api.follow_user(user_id=other_user_id)

        if follow[0].outgoing_status == 'follows':
            return True
        return False
