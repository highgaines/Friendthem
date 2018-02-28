from django.contrib import admin
from django.apps import apps
from django.urls import path, include
from rest_framework_social_oauth2 import urls as rest_framework_social_oauth2_urls

auth_name = apps.get_app_config('core_auth').verbose_name
connect_name = apps.get_app_config('connect').verbose_name
feed_name = apps.get_app_config('feed').verbose_name
pictures_name = apps.get_app_config('pictures').verbose_name
notifications_name = apps.get_app_config('notifications').verbose_name

urlpatterns = [
    path('', include(('src.core_auth.urls', auth_name), namespace='user')),
    path('auth/', include('rest_framework_social_oauth2.urls')),
    path('admin/', admin.site.urls),
    path('connect/', include(('src.connect.urls', connect_name), namespace='connect')),
    path('feed/', include(('src.feed.urls', feed_name), namespace='feed')),
    path('notifications/', include(('src.notifications.urls', notifications_name), namespace='notifications')),
    path('pictures/', include(('src.pictures.urls', pictures_name), namespace='pictures')),
]
