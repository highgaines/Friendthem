from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
from django.views import View

from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from src.invite.serializers import InviteSerializer
from src.notifications.models import Device

User = get_user_model()

class CreateInviteView(ListCreateAPIView):
    serializer_class = InviteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.invite_set.all()

class CheckInviteView(View):
    def get(self, request, user_id=None):
        user = get_object_or_404(User, id=user_id)
        return render(request, 'check_invite.html', context={'user_id': user_id})

    def post(self, request, user_id=None):
        user = get_object_or_404(User, id=user_id)
        device_exists = Device.objects.filter(
            device_id=request.POST['device-id']
        ).exists()
        if device_exists:
            return render(request, 'check_invite-fail.html')
        return render(request, 'check_invite-success.html')


invite_view = CreateInviteView.as_view()
check_invite_view = CheckInviteView.as_view()
