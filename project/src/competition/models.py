from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth import get_user_model

User = get_user_model()

FRIENDTHEM_USER_ID = 830
FRATERNITY_USER_IDS = [829, 44]
SORORITY_USER_IDS = [1567, 652]

class ListWithClone(list):
    def _clone(self):
        return self

class CompetitionUserManager(BaseUserManager):
    def get_queryset(self):
        qs = super(CompetitionUserManager, self).get_queryset()
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


    def _get_queryset(self):
        qs = super(CompetitionUserManager, self).get_queryset()
        qs = qs.annotate(
            invite_points=models.Count('invite') * 10,
            connection_from_points=models.Count('connection_user_1') * 1,
            connection_to_points=models.Count('connection_user_2') * 5
        ).annotate(
            total_points=(
                models.F('invite_points') +
                models.F('connection_from_points') +
                models.F('connection_to_points')
            ),
            social_count=models.Count('social_auth')
        )
        return qs.filter(social_count__gte=3)


class CompetitionUser(User):
    objects = CompetitionUserManager()
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
