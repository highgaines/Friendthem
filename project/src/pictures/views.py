from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from src.pictures.services import FacebookProfilePicture
from src.pictures.serializers import PictureSerializer

class FacebookPicturesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            service = FacebookProfilePicture(self.request.user)
            data = service.get_pictures()
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'data': data})

class PictureViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PictureSerializer

    def get_queryset(self):
        return self.request.user.pictures.all()

    def destroy(self, request, pk=None):
        super(PictureViewSet, self).destroy(request, pk)
        response = self.list(request)
        return response

    def create(self, request, pk=None):
        create_response = super(PictureViewSet, self).create(request, pk)
        response = self.list(request)
        response.status_code = create_response.status_code
        return response

    def update(self, request, pk=None):
        update_response = super(PictureViewSet, self).update(request, pk)
        response = self.list(request)
        response.status_code = update_response.status_code
        return response

facebook_pictures_view = FacebookPicturesView.as_view()
pictures_list_create_view = PictureViewSet.as_view({'get': 'list', 'post': 'create'})
pictures_delete_update_view = PictureViewSet.as_view({'put': 'update', 'delete': 'destroy'})
