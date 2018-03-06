import json
from copy import copy

from django.contrib.auth import get_user_model
from django.http import HttpResponse

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D

from oauth2_provider.oauth2_backends import OAuthLibCore
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.views.mixins import OAuthLibMixin

from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.views import APIView

from src.core_auth.serializers import (UserSerializer, TokenSerializer,
                                       ProfileSerializer, LocationSerializer,
                                       NearbyUsersSerializer, SocialProfileSerializer,
                                       AuthErrorSerializer, ChangePasswordSerializer)


User = get_user_model()


class RegisterUserView(OAuthLibMixin, CreateAPIView):
    model = User
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


class AuthErrorView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AuthErrorSerializer

    def get_queryset(self):
        errors = self.request.user.auth_errors.all()
        errors_copy = copy(errors)
        errors.delete()
        return errors_copy


class TokensViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TokenSerializer
    lookup_field = 'provider'
    lookup_url_kwarg = 'provider'

    def get_queryset(self):
        return self.request.user.social_auth.all()


class UpdateProfileView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user


class CreateSocialProfileView(CreateAPIView):
    serializer_class = SocialProfileSerializer
    permission_classes = [IsAuthenticated]


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

        if user.last_location:
            queryset = (User.objects.filter(
                last_location__distance_lte=(user.last_location, distance),
                ghost_mode=False) | User.objects.filter(featured=True)
            )
            last_location = user.last_location
        else:
            queryset = User.objects.filter(featured=True)
            last_location = GEOSGeometry('POINT (0 0)', srid=4326)


        return queryset.annotate(
            distance=Distance('last_location', last_location)
        ).exclude(id=self.request.user.id)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, *args, **kwargs):
        user = self.request.user

        serializer = self.serializer_class(user, data=self.request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(serializer.data)



def redirect_user_to_app(request):
    location = 'FriendThem://'
    response = HttpResponse('', status=302)
    response['Location'] = location

    return response

register_user = RegisterUserView.as_view()
user_details = UserDetailView.as_view()
tokens_list = TokensViewSet.as_view({'get': 'list'})
tokens_get = TokensViewSet.as_view({'get': 'retrieve'})
errors_list = AuthErrorView.as_view()
update_profile = UpdateProfileView.as_view()
social_profile = CreateSocialProfileView.as_view()
update_location = UpdateLocationView.as_view()
nearby_users = NearbyUsersView.as_view()
change_password = ChangePasswordView.as_view()
