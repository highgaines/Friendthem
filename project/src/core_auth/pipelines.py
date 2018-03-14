import googleapiclient.discovery, google.oauth2.credentials
from django.conf import settings

def get_user(strategy, *args, **kwargs):
    user = kwargs.get('user', strategy.request.user)
    if user.is_anonymous:
        return
    return {'user': user}

def profile_data(response, details, backend, user, social, *args, **kwargs):
    social_profile(backend, response, details, user, social)
    profile_picture(backend, response, user)


def get_last_work(work_info):
    ordered_works = sorted(
        work_info, key=lambda x: x.get('start_date', '0'), reverse=True
    )
    if ordered_works:
        return {
            'employer': ordered_works[0].get('employer', {}).get('name'),
            'occupation': ordered_works[0].get('position', {}).get('name'),
        }
    else:
        return {}

def update_user_profile_from_facebook(user, response):
    if not user.hometown:
        user.hometown = response.get('hometown',{}).get('name')
    if not user.bio:
        user.bio = response.get('about')
    if not user.age_range:
        user.age_range = '{} - {}'.format(
            response.get('age_range', {}).get('min', ''),
            response.get('age_range', {}).get('max', ''),
        )
    work = get_last_work(response.get('work', []))
    if not user.occupation:
        user.occupation = work.get('occupation')
    if not user.employer:
        user.employer = work.get('employer')
    user.save()

def social_profile(backend, response, details, user, social, *args, **kwargs):
    if backend.name == 'twitter':
        username = response.get('screen_name')
    elif backend.name == 'linkedin-oauth2':
        username = details.get('fullname')
    elif backend.name == 'facebook':
        username = response.get('name')
        update_user_profile_from_facebook(user, response)
    elif backend.name == 'google-oauth2':
        username = response.get('displayName')
    elif backend.name == 'instagram':
        username = response.get('user', {}).get('username')

    social.extra_data.update({'username': username})
    social.save()

def profile_picture(backend, response, user):
    if user.picture:
        return

    if backend.name == 'facebook':
        picture_url = 'https://graph.facebook.com/{}/picture?type=large'.format(
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
