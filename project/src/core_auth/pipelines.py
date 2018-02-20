import googleapiclient.discovery, google.oauth2.credentials
from django.conf import settings
from src.core_auth.models import SocialProfile

def profile_data(response, details, backend, user, *args, **kwargs):
    social_profile(backend, response, details, user)
    profile_picture(backend, response, user)

def social_profile(backend, response, details, user, *args, **kwargs):
    if backend.name == 'twitter':
        username = response.get('screen_name')
    elif backend.name == 'linkedin-oauth2':
        username = details.get('fullname')
    elif backend.name == 'facebook':
        username = response.get('name')
    elif backend.name == 'google-oauth2':
        username = response.get('displayName')
    elif backend.name == 'instagram':
        username = response.get('user', {}).get('username')

    SocialProfile.objects.update_or_create(
            user=user, provider=backend.name,
            defaults={'username': username}
    )

def profile_picture(backend, response, user):
    if user.picture:
        return

    if backend.name == 'facebook':
        picture_url = 'https://graph.facebook.com/{}/picture'.format(
            response.get('id')
        )
    elif backend.name == 'twitter':
        picture_url = response.get('profile_image_url', '').replace('_normal', '')
    elif backend.name == 'google-oauth2':
        picture_url = response.get('image', {}).get('url')
    elif backend.name == 'instagram':
        picture_url = response.get('user', {}).get('profile_picture')
    else:
        return

    user.picture = picture_url
    user.save()

def get_youtube_channel(strategy, backend, social, *args, **kwargs):
    if backend.name == 'google-oauth2':
        credentials = google.oauth2.credentials.Credentials(
            token=social.get_access_token(strategy),
            client_id=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            client_secret=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
        )

        service = googleapiclient.discovery.build(
            'youtube', 'v3',
            credentials=credentials
        )
        response = service.channels().list(mine=True, part='id').execute()

        if response.get('items'):
            social.set_extra_data({'youtube_channel': response['items'][0]['id']})
            social.save()
