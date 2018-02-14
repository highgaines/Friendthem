from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from src.notifications.serializers import DeviceSerializer

class AddDeviceView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DeviceSerializer

add_device_view = AddDeviceView.as_view()
