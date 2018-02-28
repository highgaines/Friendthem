from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from src.pictures.services import FacebookProfilePicture

class PicturesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            service = FacebookProfilePicture(self.request.user)
            data = service.get_pictures()
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'data': data})

pictures_view = PicturesView.as_view()
