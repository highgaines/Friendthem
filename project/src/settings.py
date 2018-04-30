"""
Django settings for src project.

Generated by 'django-admin startproject' using Django 2.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import dj_database_url
from decouple import config, Csv
from unipath import Path

BASE_DIR = Path(__file__).ancestor(2)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'rest_framework',
    'oauth2_provider',
    'social_django',
    'rest_framework_social_oauth2',
    'django_extensions',
    'phonenumber_field',
    'mapwidgets',
    'rangefilter',
    'src.core_auth',
    'src.connect',
    'src.feed',
    'src.notifications',
    'src.pictures',
    'src.invite',
    'src.competition',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'src.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'src.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config()
}
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = [
    'social_core.backends.facebook.FacebookAppOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'src.core_auth.backends.RESTStateGoogleOAuth2',
    'src.core_auth.backends.RESTStateInstagramOAuth2',
    'src.core_auth.backends.RESTStateLinkedinOAuth2',
    'src.core_auth.backends.RESTTwitterOAuth',
    'rest_framework_social_oauth2.backends.DjangoOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]
AUTH_USER_MODEL = 'core_auth.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework_social_oauth2.authentication.SocialAuthentication',
    ]
}

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR.child('static')
STATICFILES_STORAGE = config('STATICFILES_STORAGE', default='whitenoise.django.GzipManifestStaticFilesStorage')
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'npm.finders.NpmFinder',
]

# configuring media
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

OAUTH2_PROVIDER = {
    'ACCESS_TOKEN_EXPIRE_SECONDS': 3600 * 24 * 365,
}

LOGIN_REDIRECT_URL = '/redirect_to_app/'
SOCIAL_AUTH_USER_FIELDS = ['email',]

SOCIAL_AUTH_PIPELINE = [
    'src.core_auth.pipelines.get_user',
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'src.core_auth.pipelines.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'src.core_auth.pipelines.profile_data',
    'src.core_auth.pipelines.get_youtube_channel',
    'src.pictures.pipelines.autoset_user_pictures',
    'src.connect.pipelines.connect_existing_friends',
]


SOCIAL_AUTH_FACEBOOK_KEY = config('FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = config('FACEBOOK_SECRET')
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id,email,name,hometown,work,age_range,about,picture.height(2048)'
}
SOCIAL_AUTH_FACEBOOK_API_VERSION = '2.9'


SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = config('GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = config('GOOGLE_OAUTH2_SECRET')
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE =  [
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/plus.me',
    'https://www.googleapis.com/auth/plus.login',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]
SOCIAL_AUTH_GOOGLE_OAUTH2_IGNORE_DEFAULT_SCOPE = True
SOCIAL_AUTH_GOOGLE_OAUTH2_USE_DEPRECATED_API = True
SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {
   'access_type': 'offline',
}

SOCIAL_AUTH_GOOGLE_PLUS_AUTH_EXTRA_ARGUMENTS = {
   'access_type': 'offline',
}

SOCIAL_AUTH_INSTAGRAM_KEY = config('INSTAGRAM_KEY')
SOCIAL_AUTH_INSTAGRAM_SECRET = config('INSTAGRAM_SECRET')
SOCIAL_AUTH_INSTAGRAM_AUTH_EXTRA_ARGUMENTS = {'scope': 'relationships follower_list public_content'}

SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY = config('LINKEDIN_KEY')
SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET = config('LINKEDIN_SECRET')
SOCIAL_AUTH_LINKEDIN_OAUTH2_SCOPE = ['r_emailaddress,w_share']

SOCIAL_AUTH_TWITTER_KEY = config('TWITTER_KEY')
SOCIAL_AUTH_TWITTER_SECRET = config('TWITTER_SECRET')

ONESIGNAL_APP_ID = config('ONESIGNAL_APP_ID')
ONESIGNAL_APP_KEY = config('ONESIGNAL_APP_KEY')

MAP_WIDGETS = {
    'GooglePointFieldWidget': (
        ('zoom', 12),
        ('mapCenterLocationName', 'new york'),
    ),
    'GOOGLE_MAP_API_KEY': config('GOOGLE_MAPS_API_KEY')
}

GDAL_LIBRARY_PATH = config('GDAL_LIBRARY_PATH', default='')
GEOS_LIBRARY_PATH = config('GEOS_LIBRARY_PATH', default='')

INSTALLED_APPS += ('raven.contrib.django.raven_compat', )

AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = config('AWS_SECRET_KEY')
AWS_S3_BUCKET_KEY = config('AWS_S3_BUCKET_KEY')

APP_URL = 'FriendThem://'
