class BaseConnect(object):
    def __init__(self, user):
        self.user = user
        self.api = self._authenticate(self.user)

    def _authenticate(self):
        raise NotImplemented

    def connect(self, other_user):
        raise NotImplemented
