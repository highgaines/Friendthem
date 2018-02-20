from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models

from mapwidgets.widgets import GooglePointFieldWidget

User = get_user_model()
class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        ('User Data', {'fields': ('email', 'first_name', 'last_name')}),
        ('Profile', {'fields': (
            'picture', 'hobbies', 'hometown', 'occupation', 'phone_number', 'age',
            'personal_email'
        )}),
        ('Settings', {'fields': (('ghost_mode', 'notifications'),)}),
        ('Location', {'fields': ('last_location',)})
    )
    list_display = (
        'id', 'email', 'ghost_mode', 'notifications', 'latitude', 'longitude'
    )

    def latitude(self, obj):
        if obj.last_location:
            return obj.last_location.x

    def longitude(self, obj):
        if obj.last_location:
            return obj.last_location.y

    formfield_overrides = {
        models.PointField: {"widget": GooglePointFieldWidget}
    }

admin.site.register(User, UserAdmin)
