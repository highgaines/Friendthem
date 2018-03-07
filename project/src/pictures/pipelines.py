from src.pictures.services import FacebookProfilePicture

def autoset_user_pictures(backend, user, *args, **kwargs):
    if backend.name == 'facebook' and not user.pictures.all():
        service = FacebookProfilePicture(user)
        pictures = service.get_pictures()[:6]
        picture_objs = [
            user.pictures.create(url=picture['picture']) for picture in pictures
        ]
        return {'pictures': picture_objs}
