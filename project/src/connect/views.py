from django.contrib.auth import get_user_model
from django.shortcuts import get_list_or_404
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from src.connect.serializers import ConnectionSerializer, ConnectedUserSerializer
from src.connect.models import Connection

User = get_user_model()

class ConnectionAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConnectionSerializer

class ConnectionListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConnectionSerializer

    def get_queryset(self, *args, **kwargs):
        return get_list_or_404(
            Connection, user_1=self.request.user,
            user_2=self.kwargs['user_id'],
        )

class ConnectedUsersAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConnectedUserSerializer

    def get_queryset(self):
        connected_user_ids = Connection.objects.filter(
            user_1=self.request.user
        ).values_list('user_2', flat=True).distinct()

        return User.objects.filter(id__in=connected_user_ids)

connection_view = ConnectionAPIView.as_view()
connected_users_view = ConnectedUsersAPIView.as_view()
connection_list_view = ConnectionListAPIView.as_view()
