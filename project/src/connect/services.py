import twitter
from instagram import InstagramAPI, InstagramClientError

import googleapiclient.discovery, google.oauth2.credentials
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

class CredentialsNotFound(Exception):
    pass

class SocialUserNotFound(Exception):
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
            raise CredentialsNotFound

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
            raise SocialUserNotFound

        friendship = self.api.CreateFriendship(user_id=other_user_id, follow=True)


        if friendship.following:
            return True
        return False


class InstagramConnect(object):
    def __init__(self, user):
        self.api = self._authenticate(user)

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

class YoutubeConnect(object):
    def __init__(self, user):
        self.api = self._authenticate(user)

    def _authenticate(self, user):
        try:
            social_auth = user.social_auth.get(provider='google-oauth2')
            token_key = social_auth.extra_data['access_token']
        except (ObjectDoesNotExist, KeyError):
            raise CredentialsNotFound


        credentials = google.oauth2.credentials.Credentials(
            token=social_auth.extra_data['access_token'],
            client_id=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            client_secret=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
        )

        return googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)

    def connect(self, other_user):
        try:
            other_social_auth = other_user.social_auth.get(provider='google-oauth2')
            channel_id = other_social_auth.extra_data['youtube_channel']

        except (ObjectDoesNotExist, KeyError):
            raise SocialUserNotFound

        resource = {'snippet': {
            'resourceId': {
                'kind': 'youtube#channel',
                'channelId': channel_id
            }
        }}
        self.api.subscriptions().insert(body=resource, part='snippet').execute()

        return True
