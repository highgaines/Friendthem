from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Count, F
from rangefilter.filter import DateTimeRangeFilter, DateRangeFilter
from src.competition.models import CollegeCompetitionUser, CompetitionUser

User = get_user_model()

class BaseCompetitionAdmin(admin.ModelAdmin):
    search_fields = ('id', 'email', 'first_name', 'last_name')
    list_filter = (
        ('date_joined', DateRangeFilter),
    )
    readonly_fields = ('last_location', )

    def _full_name(self, obj):
        return obj.get_full_name()
    _full_name.short_description = 'Full Name'

class CollegeCompetitionAdmin(BaseCompetitionAdmin):
    list_display = (
        '_full_name', 'date_joined', 'social_sync_points', 'friendthem_points',
        'fraternity_points', 'sorority_points', 'total_points'
    )

    def friendthem_points(self, obj):
        return obj.friendthem_points
    friendthem_points.admin_order_field = 'friendthem_points'

    def fraternity_points(self, obj):
        return obj.fraternity_points
    fraternity_points.admin_order_field = 'fraternity_points'

    def sorority_points(self, obj):
        return obj.sorority_points
    sorority_points.admin_order_field = 'sorority_points'

    def social_sync_points(self, obj):
        return obj.social_sync_points
    social_sync_points.admin_order_field = 'social_sync_points'

    def total_points(self, obj):
        return obj.total_points
    total_points.admin_order_field = 'total_points'

class CompetitionAdmin(BaseCompetitionAdmin):
    list_display = (
        '_full_name', 'date_joined', 'social_sync_points', 'invitations_points',
        'received_connections_points', 'sent_connections_points', 'total_points'
    )

    def invitations_points(self, obj):
        return obj.invitations_points
    invitations_points.admin_order_field = 'invitations_points'

    def received_connections_points(self, obj):
        return obj.received_connections_points
    received_connections_points.admin_order_field = 'received_connections_points'

    def sent_connections_points(self, obj):
        return obj.sent_connections_points
    sent_connections_points.admin_order_field = 'sent_connections_points'

    def social_sync_points(self, obj):
        return obj.social_sync_points
    social_sync_points.admin_order_field = 'social_sync_points'

    def total_points(self, obj):
        return obj.total_points
    total_points.admin_order_field = 'total_points'

admin.site.register(CollegeCompetitionUser, CollegeCompetitionAdmin)
admin.site.register(CompetitionUser, CompetitionAdmin)
