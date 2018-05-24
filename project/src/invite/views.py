from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View

from rest_framework.permissions import IsAuthenticated
from src.invite.models import Invite
from src.notifications.models import Device

User = get_user_model()

class CheckInviteView(View):
    def get(self, request, user_id=None):
        user = get_object_or_404(User, id=user_id)
        return render(request, 'check_invite.html', context={'user_id': user_id})

    def post(self, request, user_id=None):
        user = get_object_or_404(User, id=user_id)
        device_id = request.POST.get('device-id')
        device_exists = Device.objects.filter(device_id=device_id).exists()
        if not device_exists:
            Invite.objects.get_or_create(user=user, device_id=device_id)
        response = HttpResponse('', status=302)
        response['Location'] = settings.STORE_URL
        return response


check_invite_view = CheckInviteView.as_view()
