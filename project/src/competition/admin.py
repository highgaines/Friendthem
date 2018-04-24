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

class CompetitionAdmin(BaseCompetitionAdmin):
    list_display = (
        '_full_name', 'date_joined', 'social_sync_points', 'invitations_points',
        'received_connections_points', 'sent_connections_points', 'total_points'
    )

class CompetitionAdminSite(admin.AdminSite):
    site_header = 'Friendthem Superconnect Competition'

competition_site = CompetitionAdminSite(name='competition_admin')
competition_site.register(CollegeCompetitionUser, CollegeCompetitionAdmin)
competition_site.register(CompetitionUser, CompetitionAdmin)
