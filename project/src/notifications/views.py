from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView
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
        return self.request.user.received_notifications.all()

class DeleteNotificationView(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return self.request.user.received_notifications.order_by(
            '-created_at', '-id'
        )

add_device_view = AddDeviceView.as_view()
notifications_view = ListNotificationsView.as_view()
delete_notification_view = DeleteNotificationView.as_view()
