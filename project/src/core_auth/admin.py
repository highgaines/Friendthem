from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from mapwidgets.widgets import GooglePointFieldWidget

from social_django.models import UserSocialAuth

User = get_user_model()

class SocialAuthInline(admin.TabularInline):
    model = UserSocialAuth
    fields = ('provider', 'uid', 'extra_data')

class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        ('User Data', {'fields': ('email', ('first_name', 'last_name'), 'featured')}),
        ('Profile', {'fields': (
            'picture', 'hobbies', 'hometown', 'occupation', 'phone_number', 'age',
            'personal_email'
        )}),
        ('Settings', {'fields': (('ghost_mode', 'notifications'),)}),
        ('Location', {'fields': ('last_location',)})
    )
    list_display = (
        'id', 'email', 'featured', 'ghost_mode', 'notifications', 'latitude', 'longitude'
    )
    list_filter = ('featured',)
    actions = ('mark_as_featured', 'unmark_as_featured')
    inlines = [SocialAuthInline]

    def latitude(self, obj):
        if obj.last_location:
            return obj.last_location.x

    def longitude(self, obj):
        if obj.last_location:
            return obj.last_location.y

    def mark_as_featured(self, request, queryset):
        msg = 'Users marked as featured.'
        queryset.update(featured=True)
        self.message_user(request, msg, messages.SUCCESS)
    mark_as_featured.shirt_description = 'Mark as featured.'

    def unmark_as_featured(self, request, queryset):
        msg = 'Users unmarked as featured.'
        queryset.update(featured=False)
        self.message_user(request, msg, messages.SUCCESS)
    mark_as_featured.shirt_description = 'Unmark as featured.'


    formfield_overrides = {
        models.PointField: {"widget": GooglePointFieldWidget}
    }

admin.site.register(User, UserAdmin)
