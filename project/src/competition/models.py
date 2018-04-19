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

class CompetitionUserQuerySet(models.query.QuerySet):
    def order_by(self, *field_names):
        field_names = list(field_names)
        property_fields = [
            'friendthem_points', 'fraternity_points',
            'sorority_points', 'social_sync_points', 'total_points',
        ]
        property_fields += [f'-{field}' for field in property_fields]
        property_orderings = []
        for prop in property_fields:
            if prop in field_names:
                property_orderings.append(field_names.pop(field_names.index(prop)))

        objs = super(CompetitionUserQuerySet, self).order_by(*field_names)

        for prop in property_orderings:
            field = prop.strip('-')
            objs = ListWithClone(
                sorted(objs, key=lambda x: getattr(x, field)(), reverse=prop.startswith('-'))
            )

        return objs


class CompetitionUserManager(BaseUserManager):
    def get_queryset(self):
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
    objects = CompetitionUserQuerySet.as_manager()
    class Meta:
        proxy = True

    def friendthem_points(self):
        if self._friendthem_points is None:
            self._friendthem_points = self.connection_user_1.filter(
                user_2=FRIENDTHEM_USER_ID
            ).distinct('user_2').count()
        return self._friendthem_points
    friendthem_points.admin_order_field = 'friendthem_points'
    _friendthem_points = None

    def fraternity_points(self):
        if self._fraternity_points is None:
            self._fraternity_points = self.connection_user_1.filter(
                user_2__in=FRATERNITY_USER_IDS
            ).distinct('user_2').count()

        return self._fraternity_points
    fraternity_points.admin_order_field = 'fraternity_points'
    _fraternity_points = None

    def sorority_points(self):
        if self._sorority_points is None:
            self._sorority_points = self.connection_user_1.filter(
                user_2__in=SORORITY_USER_IDS
            ).distinct('user_2').count()
        return self._sorority_points
    sorority_points.admin_order_field = 'sorority_points'
    _sorority_points = None

    def social_sync_points(self):
        if self._social_sync_points is None:
            if self.social_auth.count() >= 3:
                self._social_sync_points = 2
            else:
                self._social_sync_points = 0
        return self._social_sync_points
    social_sync_points.admin_order_field = 'social_sync_points'
    _social_sync_points = None

    def total_points(self):
        if self._total_points is None:
            self._total_points = sum([
                self.friendthem_points(), self.fraternity_points(),
                self.sorority_points(), self.social_sync_points()
            ])
        return self._total_points
    total_points.admin_order_field = 'total_points'
    _total_points = None
