from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

import googleapiclient.discovery, google.oauth2.credentials
from src.connect.services.base import BaseConnect
from src.connect.exceptions import CredentialsNotFound, SocialUserNotFound

class YoutubeConnect(BaseConnect):
    def _authenticate(self, user):
        try:
            social_auth = user.social_auth.get(provider='google-oauth2')
            token_key = social_auth.extra_data['access_token']
        except (ObjectDoesNotExist, KeyError):
            raise CredentialsNotFound('google-oauth2', user)

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
            raise SocialUserNotFound('google-oauth2', other_user)

        resource = {'snippet': {
            'resourceId': {
                'kind': 'youtube#channel',
                'channelId': channel_id
            }
        }}
        self.api.subscriptions().insert(body=resource, part='snippet').execute()

        return True
