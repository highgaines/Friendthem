from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from src.connect.serializers import ConnectionSerializer

class ConnectionAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConnectionSerializer

connection_view = ConnectionAPIView.as_view()
