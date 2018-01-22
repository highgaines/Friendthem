from src.core_auth.models import SocialProfile

def get_user(strategy, *args, **kwargs):
    user = strategy.request.user
    if user.is_anonymous:
        return
    return {'user': user}

def social_profile(strategy, response, details, backend, user, *args, **kwargs):
    if backend.name == 'twitter':
        username = response.get('screen_name')
    elif backend.name == 'linkedin-oauth2':
        username = details.get('fullname')
    elif backend.name == 'facebook':
        username = response.get('name')
    elif backend.name == 'google-oauth2':
        username = response.get('displayName')
    elif backend.name == 'instagram':
        username = response.get('username')

    profile = SocialProfile.objects.update_or_create(
            user=user, provider=backend.name, defaults={'username': username}
    )
