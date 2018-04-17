from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from src.invite.serializers import InviteSerializer

class CreateInviteView(ListCreateAPIView):
    serializer_class = InviteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.invite_set.all()

invite_view = CreateInviteView.as_view()
