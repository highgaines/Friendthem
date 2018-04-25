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

    class Meta:
        proxy = True


class CompetitionUserManager(BaseUserManager):
    def get_queryset(self):
        qs = super(CompetitionUserManager, self).get_queryset()
        qs = qs.annotate(
            social_count=models.Count('social_auth'),
            received_connections=models.Count('connection_user_2__user_1'),
            sent_connections=models.Count('connection_user_1__user_2'),
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

    class Meta:
        proxy = True
