from urllib.parse import urlparse
import facebook

class FacebookProfilePicture(object):
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

    def get_profile_picture_album(self):
        albums = self.api.get_connections('me', 'albums')
        return [album for album in albums if album['name'] == 'Profile Pictures'][0]

    def get_pictures(self):
        album = self.get_profile_picture_album()
        response = self.api.get_connections(album['id'], 'photos', fields='picture', limit=200)
        return [
            {
                'id': d['id'],
                'picture': sanitize_picture_url(d['picture'])
            } for d in response['data']
        ]

    @staticmethod
    def sanitize_picture_url(url):
        parsed = urlparse(url)
        return '{}://{}/{}'.format(parsed.scheme, parsed.netloc, parsed.path)
