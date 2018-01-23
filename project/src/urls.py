"""src URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.apps import apps
from django.urls import path, include
from rest_framework_social_oauth2 import urls as rest_framework_social_oauth2_urls

auth_name = apps.get_app_config('core_auth').verbose_name

urlpatterns = [
    path('/', include(('src.core_auth.urls', auth_name), namespace='user')),
    path('auth/', include('rest_framework_social_oauth2.urls')),
    path('admin/', admin.site.urls),
]
