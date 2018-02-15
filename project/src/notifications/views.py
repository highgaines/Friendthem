from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from src.notifications.serializers import DeviceSerializer, NotificationSerializer

class AddDeviceView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DeviceSerializer

class ListNotificationsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        self.request.user.received_notifications.all()

add_device_view = AddDeviceView.as_view()
notifications_view = ListNotificationsView.as_view()
