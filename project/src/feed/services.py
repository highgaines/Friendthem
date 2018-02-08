import requests, facebook, maya
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
        self.api = self.authenticate(user)

    def authenticate(self, user):
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
