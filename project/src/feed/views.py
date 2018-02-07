from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from src.feed.services import FacebookFeed, InstagramFeed

User = get_user_model()

class FeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, format=None):
        other_user = get_object_or_404(
            User, id=user_id
        )
        data = []
        errors = {}
        for Service in [FacebookFeed, InstagramFeed]:
            try:
                service = Service(self.request.user)
                data += service.get_feed('user')
            except Exception as err:
                errors.update({service.provider: err})

        data = sorted(data, key=lambda x: x.get('created_time', 0), reverse=True)
        return Response({'data': data, 'errors': errors})


feed_view = FeedView.as_view()
