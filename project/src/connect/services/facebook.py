import facebook, requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from social_django.models import UserSocialAuth

from src.connect.exceptions import CredentialsNotFound
from src.connect.models import Connection
from src.connect.services.dummy import DummyConnect

class FacebookConnect(DummyConnect):
    provider = 'facebook'
    def _authenticate(self, user):
        try:
            access_token = user.social_auth.get(
                provider=self.provider
            ).extra_data['access_token']
        except (KeyError, ObjectDoesNotExist):
            raise CredentialsNotFound(self.provider, user)

        return facebook.GraphAPI(
            access_token,
            version=settings.SOCIAL_AUTH_FACEBOOK_API_VERSION
        )

    def connect_users(self):
        connections = []
        friends_data = self.api.get_connections('me', 'friends', fields='id', limit=500)
        friends = [data['id'] for data in friends_data['data']]
        while True:
            try:
                _next = friends_data['paging']['next']
                friends_data = requests.get(_next).json()
                friends += [data['id'] for data in friends_data['data']]
            except KeyError:
                break

        existing_friends = UserSocialAuth.objects.filter(uid__in=friends, provider=self.provider)
        for friend in existing_friends:
            other_user = friend.user
            connections.append(
                Connection.objects.update_or_create(
                user_1=self.user, user_2=other_user,
                provider=self.provider, defaults={'confirmed': True}
                )[0]
            )

        return connections

    def get_existing_friends(self):
        connections = []
        friends_data = self.api.get_connections('me', 'friends', fields='id', limit=500)
        friends = [data['id'] for data in friends_data['data']]
        while True:
            try:
                _next = friends_data['paging']['next']
                friends_data = requests.get(_next).json()
                friends += [data['id'] for data in friends_data['data']]
            except KeyError:
                break

        return UserSocialAuth.objects.filter(uid__in=friends, provider=self.provider)

