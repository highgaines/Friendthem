from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Count, F
from rangefilter.filter import DateTimeRangeFilter, DateRangeFilter
from src.competition.models import CompetitionUser

User = get_user_model()

class FraternityCompetitionAdmin(admin.ModelAdmin):
    list_display = (
        'get_full_name', 'date_joined', 'social_sync_points', 'friendthem_points',
        'fraternity_points', 'sorority_points', 'total_points'
    )
    list_filter = (
        ('date_joined', DateRangeFilter),
    )


class CompetitionAdminSite(admin.AdminSite):
    site_header = 'Friendthem Superconnect Competition'

competition_site = CompetitionAdminSite(name='competition_admin')
competition_site.register(CompetitionUser, FraternityCompetitionAdmin)
