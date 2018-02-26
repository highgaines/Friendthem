from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from src.feed import services

User = get_user_model()

class FeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, provider, format=None):
        other_user = get_object_or_404(
            User, id=user_id
        )
        data = []
        errors = {}

        try:
            Service = getattr(services, '{}Feed'.format(provider.capitalize()))
        except AttributeError:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            service = Service(self.request.user)
            data += service.get_feed(other_user)
        except Exception as err:
            return Response({'error', str(err)}, status=status.HTTP_400_BAD_REQUEST)

        data = sorted(data, key=lambda x: x.get('created_time', 0), reverse=True)
        return Response({'data': data, 'user_id': user_id})


feed_view = FeedView.as_view()
