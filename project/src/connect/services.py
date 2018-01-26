import twitter
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

class TwitterCredentialsNotFound(Exception):
    pass

class TwitterUserNotFound(Exception):
    pass

class TwitterConnect(object):
    def __init__(self, user):
        self.api = self._authenticate(user)

    def _authenticate(self, user):
        try:
            social_auth = user.social_auth.get(provider='twitter')
            token_key = social_auth.extra_data.get('access_token', {})['oauth_token']
            token_secret =  social_auth.extra_data.get('access_token', {})['oauth_token_secret']
        except (ObjectDoesNotExist, KeyError):
            raise TwitterCredentialsNotFound

        return twitter.Api(
            consumer_key=settings.SOCIAL_AUTH_TWITTER_KEY,
            consumer_secret=settings.SOCIAL_AUTH_TWITTER_SECRET,
            access_token_key=token_key, access_token_secret=token_secret,
        )

    def connect(self, other_user):
        try:
            other_social_auth = other_user.social_auth.get(provider='twitter')
            other_user_id = other_social_auth.uid
            if not other_user_id:
                raise ObjectDoesNotExist
        except ObjectDoesNotExist:
            raise TwitterUserNotFound

        friendship = self.api.CreateFriendship(user_id=other_user_id, follow=True)


        if friendship.following:
            return True
        return False
