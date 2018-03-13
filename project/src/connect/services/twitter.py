import twitter

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from social_django.models import UserSocialAuth
from src.connect.services.base import BaseConnect
from src.connect.exceptions import CredentialsNotFound, SocialUserNotFound
from src.connect.models import Connection

class TwitterConnect(BaseConnect):
    def _authenticate(self, user):
        try:
            social_auth = user.social_auth.get(provider='twitter')
            token_key = social_auth.extra_data.get('access_token', {})['oauth_token']
            token_secret =  social_auth.extra_data.get('access_token', {})['oauth_token_secret']
        except (ObjectDoesNotExist, KeyError):
            raise CredentialsNotFound('twitter', user)

        return twitter.Api(
            consumer_key=settings.SOCIAL_AUTH_TWITTER_KEY,
            consumer_secret=settings.SOCIAL_AUTH_TWITTER_SECRET,
            access_token_key=token_key, access_token_secret=token_secret,
        )

    def connect(self, other_user):
        try:
            other_social_auth = other_user.social_auth.get(provider='twitter')
            other_user_id = other_social_auth.uid
        except ObjectDoesNotExist:
            raise SocialUserNotFound('twitter', other_user)

        friendship = self.api.CreateFriendship(user_id=other_user_id, follow=True)

        if friendship.following:
            return True
        return False

    def connect_users(self):
        connections = []
        friends = []
        cursor = -1
        while True:
            cursor, previous, twitter_users = self.api.GetFriendIDsPaged(cursor)
            friends +=  [ u.id_str for u in twitter_users ]
            if cursor is None:
                break;

        existing_friends = UserSocialAuth.objects.filter(
            provider='twitter', uid__in=friends
        )
        for friend in existing_friends:
            other_user = friend.user
            connection, _ = Connection.objects.update_or_create(
                user_1=self.user, user_2=other_user, provider='twitter'
            )
            connections.append(connection)

        return connections
