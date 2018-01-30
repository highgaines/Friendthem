class CredentialsNotFound(Exception):
    def __init__(self, provider, user):
        self.message = 'Credentials not found for user "{}" in provider "{}".'.format(
            user.id, provider
        )

class SocialUserNotFound(Exception):
    def __init__(self, provider, user):
        self.message = 'User with id "{}" not found for provider "{}".'.format(
            user.id, provider
        )

