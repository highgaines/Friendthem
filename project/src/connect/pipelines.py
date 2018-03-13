from src.connect import services

def connect_existing_friends(backend, user, *args, **kwargs):
    backend_name = backend.name
    if backend.name == 'twitter-oauth2':
        backend_name = 'twitter'
    elif backend.name == 'google-oauth2':
        backend_name = 'youtube'

    connect_class = getattr(
        services,
        f'{backend_name.capitalize()}Connect',
        services.DummyConnect
    )
    connect = connect_class(user)
    connect.connect_users()

