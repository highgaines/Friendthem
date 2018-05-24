from django.core.management.base import BaseCommand

from src.core_auth.models import User
from social_django.models import UserSocialAuth
from src.connect.models import Connection
from src.connect.services.facebook import FacebookConnect
from src.connect.services.instagram import InstagramConnect

class Command(BaseCommand):
    help = 'python project/manage.py clear_user_social_account_connections'

    def handle(self, *args, **options):
        for user in User.objects.filter(id__in=[4, 5]):
            #instagram_connect = InstagramConnect(user)
            fb_connect = FacebookConnect(user)
            existing_friends = fb_connect.get_existing_friends()

            if not any(i.user_id == 4 or i.user_id == 5 for i in existing_friends):
                self.delete_existing_social_auth_and_connections()


    def delete_existing_social_auth_and_connections(self):
        Connection.objects.filter(user_1_id__in=[4, 5], user_2_id__in=[4, 5]).delete()
        UserSocialAuth.objects.filter(user_id__in=[4, 5]).delete()

