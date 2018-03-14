import time
import googleapiclient.discovery, google.oauth2.credentials

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from social_django.models import UserSocialAuth
from social_django.utils import load_strategy

from src.connect.exceptions import CredentialsNotFound, SocialUserNotFound
from src.connect.models import Connection
from src.connect.services.dummy import DummyConnect

class YoutubeConnect(DummyConnect):
    def _authenticate(self, user):
        try:
            social_auth = user.social_auth.get(provider='google-oauth2')
            token_key = social_auth.extra_data['access_token']
        except (ObjectDoesNotExist, KeyError):
            raise CredentialsNotFound('google-oauth2', user)

        expiration_time = (
            social_auth.extra_data.get('authtime', 0)
            + social_auth.extra_data.get('expires', 0)
        )
        if  expiration_time > int(time.time()):
            social_auth.refresh_token(load_strategy())

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

    def connect_users(self):
        connections = []
        channels_data = self.api.subscriptions().list(
            part='snippet', mine=True, maxResults=50
        ).execute()
        channels_ids = [
            data['snippet']['resourceId']['channelId'] for data in
            channels_data['items']
            if data['snippet']['resourceId']['kind'] == 'youtube#channel'
        ]
        while True:
            try:
                next_page_token = channels_data['nextPageToken']
                channels_data = self.api.subscriptions().list(
                    part='snippet', mine=True, maxResults=50,
                    pageToken=next_page_token
                ).execute()
                channels_ids += [
                    data['snippet']['resourceId']['channelId'] for data in
                    channels_data['items']
                    if data['snippet']['resourceId']['kind'] == 'youtube#channel'
                ]
            except KeyError:
                break

        if not channels_ids:
            return []

        channels_ids_regex = '({})'.format('|'.join(channels_ids))
        existing_friends = UserSocialAuth.objects.filter(
            provider='google-oauth2',
            extra_data__regex=channels_ids_regex
        )
        for friend in existing_friends:
            other_user = friend.user
            connection, _ = Connection.objects.update_or_create(
                user_1=self.user, user_2=other_user,
                provider='youtube', defaults={'confirmed': True}
            )
            connections.append(connection)

        return connections
