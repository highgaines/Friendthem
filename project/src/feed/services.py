import facebook, maya, requests, twitter

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from src.connect.exceptions import CredentialsNotFound, SocialUserNotFound

class InstagramFeed(object):
    '''
    This class does not use the Instagram python client because
    it's not working for its goal.
    '''
    provider = 'instagram'
    def __init__(self, user):
        try:
            self.access_token = user.social_auth.get(
                provider='instagram'
            ).extra_data['access_token']
        except (KeyError, ObjectDoesNotExist):
            raise CredentialsNotFound(self.provider, user)

    def get_feed(self, other_user):
        try:
            other_user_uid = other_user.social_auth.get(provider='instagram').uid
        except ObjectDoesNotExist:
            raise SocialUserNotFound(self.provider, other_user)

        response = requests.get(
            'https://api.instagram.com/v1/users/{}/media/recent'.format(other_user_uid),
            params={'access_token': self.access_token}
        )
        content = response.json()

        return [self.format_data(d) for d in content['data']]

    @staticmethod
    def format_data(item):
        caption = item.get('caption') or {}
        return {
            'img_url': item['images']['standard_resolution']['url'],
            'num_likes': item['likes']['count'],
            'description': caption.get('text'),
            'date_posted': int(item['created_time']),
            'type': item['type'],
            'provider': 'instagram',
        }


class FacebookFeed(object):
    provider = 'facebook'
    def __init__(self, user):
        self.api = self._authenticate(user)

    def _authenticate(self, user):
        try:
            access_token = user.social_auth.get(
                provider='facebook'
            ).extra_data['access_token']
        except (KeyError, ObjectDoesNotExist):
            raise CredentialsNotFound(self.provider, user)

        return facebook.GraphAPI(access_token)

    def get_feed(self, other_user):
        try:
            other_user_uid = other_user.social_auth.get(provider='facebook').uid
        except ObjectDoesNotExist:
            raise SocialUserNotFound(self.provider, other_user)

        fields = [
            'likes.summary(true)', 'caption', 'description', 'link',
            'name', 'picture', 'created_time', 'status_type', 'message',
        ]
        content = self.api.get_connections(other_user_uid, 'posts', fields=','.join(fields))
        return [self.format_data(d) for d in content['data']]

    @staticmethod
    def format_data(item):
        return {
            'img_url': item.get('picture'),
            'num_likes': item['likes']['summary']['total_count'],
            'description': item.get('name') or item.get('message'),
            'date_posted': int(maya.parse(item['created_time']).epoch),
            'type': item['status_type'],
            'provider': 'facebook',
        }


class TwitterFeed(object):
    provider = 'twitter'
    def __init__(self, user):
        self.api = self._authenticate(user)

    def _authenticate(self, user):
        try:
            social_auth = user.social_auth.get(provider=self.provider)
            token_key = social_auth.extra_data.get('access_token', {})['oauth_token']
            token_secret =  social_auth.extra_data.get('access_token', {})['oauth_token_secret']
        except (ObjectDoesNotExist, KeyError):
            raise CredentialsNotFound(self.provider, user)

        return twitter.Api(
            consumer_key=settings.SOCIAL_AUTH_TWITTER_KEY,
            consumer_secret=settings.SOCIAL_AUTH_TWITTER_SECRET,
            access_token_key=token_key, access_token_secret=token_secret,
        )

    def get_feed(self, other_user):

        try:
            other_user_uid = other_user.social_auth.get(provider=self.provider).uid
        except ObjectDoesNotExist:
            raise SocialUserNotFound(self.provider, other_user)

        content = self.api.GetUserTimeline(user_id=other_user_uid)

        return [self.format_data(status) for status in content]

    @staticmethod
    def format_data(item):
        img_url = None
        _type = 'status'
        if item.media:
            media_url = item.media[0].media_url_https
            _type = item.media[0].type

        return {
            'img_url': img_url,
            'num_likes': item.favorite_count,
            'description': item.text,
            'date_posted': item.created_at_in_seconds,
            'type': _type,
            'provider': 'twitter',
        }
