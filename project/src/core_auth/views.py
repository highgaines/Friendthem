import json

from django.contrib.auth import get_user_model
from django.http import HttpResponse

from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from oauth2_provider.oauth2_backends import OAuthLibCore
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.views.mixins import OAuthLibMixin

from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from src.core_auth.serializers import (UserSerializer, TokenSerializer,
                                       HobbiesSerializer, LocationSerializer,
                                       NearbyUsersSerializer)


class RegisterUserView(OAuthLibMixin, CreateAPIView):
    model = get_user_model()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    server_class = oauth2_settings.OAUTH2_SERVER_CLASS
    validator_class = oauth2_settings.OAUTH2_VALIDATOR_CLASS
    oauthlib_backend_class = OAuthLibCore

    def create(self, request, *args, **kwargs):
        request._request.POST = request._request.POST.copy()
        for key, value in request.data.items():
            request._request.POST[key] = value

        super(RegisterUserView, self).create(request, *args, **kwargs)
        url, headers, body, status = self.create_token_response(request._request)
        response = Response(data=json.loads(body), status=status)

        for k, v in headers.items():
            response[k] = v

        return response


class UserDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class TokensViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TokenSerializer
    lookup_field = 'provider'
    lookup_url_kwarg = 'provider'

    def get_queryset(self):
        return self.request.user.social_auth.all()


def redirect_user_to_app(request):
    location = 'FriendThem://'
    response = HttpResponse('', status=302)
    response['Location'] = location

    return response


class UpdateHobbiesView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HobbiesSerializer

    def get_object(self):
        return self.request.user


class UpdateLocationView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LocationSerializer

    def get_object(self):
        return self.request.user

class NearbyUsersView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NearbyUsersSerializer

    def get_queryset(self):
        user = self.request.user
        miles = self.request.GET.get('miles', 200)
        distance = D(mi=miles)

        return get_user_model().objects.filter(
            last_location__distance_lte=(user.last_location, distance)
        ).annotate(
            distance=Distance('last_location', user.last_location)
        ).exclude(id=self.request.user.id)


register_user = RegisterUserView.as_view()
user_details = UserDetailView.as_view()
tokens_list = TokensViewSet.as_view({'get': 'list'})
tokens_get = TokensViewSet.as_view({'get': 'retrieve'})
update_hobbies = UpdateHobbiesView.as_view()
update_location = UpdateLocationView.as_view()
nearby_users = NearbyUsersView.as_view()
