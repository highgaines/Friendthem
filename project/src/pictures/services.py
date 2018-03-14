from urllib.parse import urlparse
import facebook

from django.core.exceptions import ObjectDoesNotExist
from src.connect.exceptions import CredentialsNotFound
from src.pictures.exceptions import ProfilePicturesAlbumNotFound


class FacebookProfilePicture(object):
    provider = 'facebook'
    def __init__(self, user=None, access_token=None):
        self.api = self._authenticate(user, access_token)

    def _authenticate(self, user, access_token=None):
        if user and not access_token:
            try:
                access_token = user.social_auth.get(
                    provider=self.provider
                ).extra_data['access_token']
            except (KeyError, ObjectDoesNotExist):
                raise CredentialsNotFound(self.provider, user)

        return facebook.GraphAPI(access_token)

    def get_profile_picture_album(self, uid=None):
        if not uid:
            uid = 'me'
        response = self.api.get_connections(uid, 'albums', limit=1000)
        try:
            return [album for album in response['data'] if album['name'] == 'Profile Pictures'][0]
        except IndexError:
            raise ProfilePicturesAlbumNotFound('Could not find album with name equals to "Profile Pictures"')

    def get_pictures(self, uid=None):
        album = self.get_profile_picture_album(uid)
        response = self.api.get_connections(album['id'], 'photos', fields='images', limit=200)
        return [
            {'id': d['id'], 'picture': self.get_hires_picture(d) } for d in response['data']
        ]

    @staticmethod
    def get_hires_picture(data):
        sorted_images = sorted(data['images'], key=lambda x: x['height'], reverse=True)
        return sorted_images[0]['source']
