from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth import get_user_model

User = get_user_model()

FRIENDTHEM_USER_ID = 830
FRATERNITY_USER_IDS = [829, 44]
SORORITY_USER_IDS = [1567, 652]

class CollegeCompetitionUserManager(BaseUserManager):
    def get_queryset(self):
        qs = super(CollegeCompetitionUserManager, self).get_queryset()
        qs = qs.annotate(
            social_count=models.Count('social_auth'),
            friendthem_points=models.Count(
                'connection_user_1__user_2',
                filter=models.Q(connection_user_1__user_2=FRIENDTHEM_USER_ID),
                distinct=True
            ),
            fraternity_points=models.Count(
                'connection_user_1__user_2',
                filter=models.Q(connection_user_1__user_2__in=FRATERNITY_USER_IDS),
                distinct=True
            ),
            sorority_points=models.Count(
                'connection_user_1__user_2',
                filter=models.Q(connection_user_1__user_2__in=SORORITY_USER_IDS),
                distinct=True
            ),
            social_sync_points=models.Case(
                models.When(social_count__gte=3, then=2),
                default=0,
                output_field=models.IntegerField()
            ),
            total_points=models.F('social_sync_points') + \
                         models.F('sorority_points') + \
                         models.F('fraternity_points') +
                         models.F('friendthem_points')
        )
        return qs


class CollegeCompetitionUser(User):
    objects = CollegeCompetitionUserManager()

    def friendthem_points(self):
        return obj.friendthem_points
    friendthem_points.admin_order_field = 'friendthem_points'

    def fraternity_points(self):
        return obj.fraternity_points
    fraternity_points.admin_order_field = 'fraternity_points'

    def sorority_points(self):
        return obj.sorority_points
    sorority_points.admin_order_field = 'sorority_points'

    def social_sync_points(self):
        return obj.social_sync_points
    social_sync_points.admin_order_field = 'social_sync_points'

    def total_points(self):
        return obj.total_points
    total_points.admin_order_field = 'total_points'

    class Meta:
        proxy = True


class CompetitionUserManager(BaseUserManager):
    def get_queryset(self):
        qs = super(CompetitionUserManager, self).get_queryset()
        qs = qs.annotate(
            social_count=models.Count('social_auth'),
            received_connections=models.Count(
                'connection_user_2__user_1', distinct=True
            ),
            sent_connections=models.Count(
                'connection_user_1__user_2', distinct=True
            ),
            invites=models.Count('invite'),
            sent_connections_points=models.F('sent_connections') * 2,
            received_connections_points=models.F('received_connections') * 10,
            invitations_points=models.F('invites') * 100,
            social_sync_points=models.Case(
                models.When(social_count__gte=3, then=33),
                default=0,
                output_field=models.IntegerField()
            ),
            total_points=models.F('social_sync_points') + \
                         models.F('received_connections_points') + \
                         models.F('sent_connections_points') +
                         models.F('invitations_points')
        )
        return qs


class CompetitionUser(User):
    objects = CompetitionUserManager()

    def invitations_points(self):
        return obj.invitations_points
    invitations_points.admin_order_field = 'invitations_points'

    def received_connections_points(self):
        return obj.received_connections_points
    received_connections_points.admin_order_field = 'received_connections_points'

    def sent_connections_points(self):
        return obj.sent_connections_points
    sent_connections_points.admin_order_field = 'sent_connections_points'

    def social_sync_points(self):
        return obj.social_sync_points
    social_sync_points.admin_order_field = 'social_sync_points'

    def total_points(self):
        return obj.total_points
    total_points.admin_order_field = 'total_points'

    class Meta:
        proxy = True
