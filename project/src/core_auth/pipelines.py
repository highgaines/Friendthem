import random, string, logging
import boto, facebook, requests
import googleapiclient.discovery, google.oauth2.credentials
from boto.s3.key import Key

from django.conf import settings

from src.core_auth.exceptions import YoutubeChannelNotFound

USER_FIELDS = ['username', 'email']

def get_user(strategy, *args, **kwargs):
    user = kwargs.get('user', strategy.request.user)
    if user.is_anonymous:
        return
    return {'user': user}

def create_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}

    fields = dict((name, kwargs.get(name, details.get(name)))
                  for name in backend.setting('USER_FIELDS', USER_FIELDS))

    if not fields.get('email') and backend.name == 'facebook':
        letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
        prefix = ''.join(random.choices(letters, k=32))
        email = f'{prefix}@facebook.com'
        fields.update({'email': email, 'is_random_email': True})

    if not fields:
        return

    return {
        'is_new': True,
        'user': strategy.create_user(**fields)
    }

def profile_data(response, details, backend, user, social, *args, **kwargs):
    social_profile(backend, response, details, user, social)
    profile_picture(backend, response, user, social)


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

def get_picture_s3_url(backend, social, user, key, response):
    if backend.name == 'facebook':
        api = facebook.GraphAPI(
            social.extra_data['access_token'],
            version=settings.SOCIAL_AUTH_FACEBOOK_API_VERSION
        )
        picture_data = api.get_connections('me', 'picture?height=2048')
        key.key = 'profile-pic-{}.png'.format(user.id)
        key.content_type = picture_data['mime-type']
        key.set_contents_from_string(picture_data['data'])
    elif backend.name == 'instagram':
        picture_url = response.get('user', {}).get('profile_picture')
        if not picture_url:
            return
        picture_response = requests.get(picture_url)
        key.key = 'profile-pic-{}.png'.format(user.id)
        key.content_type = picture_response.content
        key.set_contents_from_string(picture_response)

    key.make_public()
    return key.generate_url(expires_in=0, query_auth=False)

def profile_picture(backend, response, user, social):
    if user.picture:
        return

    if backend.name == 'facebook' or backend.name == 'instagram':
        try:
            s3 = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_KEY)
            bucket = s3.get_bucket(settings.AWS_S3_BUCKET_KEY)
            key = Key(bucket)
            picture_url = get_picture_s3_url(backend, social, user, key, response)
        except Exception as err:
            logger = logging.getLogger(__name__)
            logger.error(
                f'Could not save Facebook profile picture on s3 for user {user}. - {err}'
            )
            picture_url = None
    elif backend.name == 'twitter':
        picture_url = response.get('profile_image_url', '').replace('_normal', '')
    elif backend.name == 'google-oauth2':
        picture_url = response.get('image', {}).get('url')
    else:
        return

    user.picture = picture_url
    user.save()



def get_youtube_channel(strategy, backend, social, *args, **kwargs):
    if backend.name == 'google-oauth2' and not social.extra_data.get('youtube_channel'):
        credentials = google.oauth2.credentials.Credentials(
            token=social.get_access_token(strategy),
            refresh_token=social.extra_data.get('refresh_token'),
            client_id=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            client_secret=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
        )

        service = googleapiclient.discovery.build(
            'youtube', 'v3',
            credentials=credentials
        )
        response = service.channels().list(mine=True, part='id,status').execute()


        if response.get('items') and response['items'][0]['status']['privacyStatus'] == 'public':
            social.set_extra_data({'youtube_channel': response['items'][0]['id']})
            social.save()
        else:
            social.delete()
            raise YoutubeChannelNotFound()
