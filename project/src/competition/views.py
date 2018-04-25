from django.shortcuts import get_object_or_404

from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from src.competition.models import CompetitionUser
from src.competition.serializers import CompetitionUserSerializer

class CompetitionUserRetrieveView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompetitionUserSerializer

    def get_object(self):
        user_id = self.request.user.id
        if 'user_id' in self.kwargs:
            user_id = self.kwargs['user_id']
        return get_object_or_404(CompetitionUser, id=user_id)

retrieve_competition_user = CompetitionUserRetrieveView.as_view()
