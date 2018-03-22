from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from src.feed import services
from src.connect.exceptions import SocialUserNotFound, CredentialsNotFound
from src.connect.models import Connection

User = get_user_model()

class FeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, provider, format=None):
        other_user = get_object_or_404(
            User, id=user_id
        )

        try:
            Service = getattr(services, '{}Feed'.format(provider.capitalize()))
        except AttributeError:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            service = Service(self.request.user)
            data = service.get_feed(other_user)
            if not data:
                connected = Connection.objects.filter(
                    provider=provider,
                    user_1=self.request.user,
                    user_2=other_user).exists()
                if not connected:
                    msg = f'User {other_user.id} has private feed and is not connected.'
                    return Response({'error': msg}, status=status.HTTP_400_BAD_REQUEST)
        except (SocialUserNotFound, CredentialsNotFound):
            return Response({'error', str(err)}, status=status.HTTP_400_BAD_REQUEST)

        data = sorted(data, key=lambda x: x.get('created_time', 0), reverse=True)
        return Response({'data': data, 'user_id': user_id})


feed_view = FeedView.as_view()
