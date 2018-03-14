from src.connect.services.base import BaseConnect
class DummyConnect(BaseConnect):
    def _authenticate(self, user):
        pass

    def connect(self, other_user):
        return False

    def connect_users(self):
        return []
