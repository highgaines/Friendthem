from src.connect import services

def connect_existing_friends(backend, user, *args, **kwargs):
    connect_class = getattr(
        services,
        f'{backend.name.capitalize()}Connect',
        services.DummyConnect
    )
    connect = connect_class(user)
    connect.connect_users()

