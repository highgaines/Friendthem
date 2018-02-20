from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models

from mapwidgets.widgets import GooglePointFieldWidget

User = get_user_model()
class UserAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.PointField: {"widget": GooglePointFieldWidget}
    }

admin.site.register(User, UserAdmin)
