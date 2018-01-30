class BaseConnect(object):
    def __init__(self, user):
        self.api = self._authenticate(user)

    def _authenticate(self):
        raise NotImplemented

    def connect(self, other_user):
        raise NotImplemented
