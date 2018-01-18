import json
from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model

from oauth2_provider.oauth2_backends import OAuthLibCore
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.views.mixins import OAuthLibMixin

from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from src.core_auth.serializers import UserSerializer

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

        user = super(RegisterUserView, self).create(request, *args, **kwargs)
        url, headers, body, status = self.create_token_response(request._request)
        response = Response(data=json.loads(body), status=status)

        for k, v in headers.items():
            response[k] = v
        return response

register_user = RegisterUserView.as_view()
