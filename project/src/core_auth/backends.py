from six.moves.urllib_parse import urlencode

from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.db import SessionStore
from django.shortcuts import redirect
from django.urls import reverse

from rest_framework.response import Response
from rest_framework.decorators import api_view

from social_core.backends.instagram import InstagramOAuth2
from social_core.backends.linkedin import LinkedinOAuth2
from social_core.backends.twitter import TwitterOAuth
from social_core.backends.google import GoogleOAuth2
from social_core.utils import url_add_parameters, parse_qs
from social_core.exceptions import AuthTokenError, AuthCanceled, AuthAlreadyAssociated

from src.core_auth.models import AuthError
from src.core_auth.exceptions import YoutubeChannelNotFound

User = get_user_model()

class RESTStateOAuth2Mixin(object):
    """This authentication backend saves the oauth flow data in a separate session
    in the start step. This data will used in complete step of the OAuth Flow."""
    def start(self):
        """
        Sends back the authentication url for the client app instead of
        redirecting the user.
        """
        return JsonResponse({'redirect_url': self.auth_url()})

    def validate_state(self):
        self.session = SessionStore(session_key=self.data.get('state'))
        return self.session.session_key

    def get_unauthorized_token(self):
        """Get unauthorized token from session passed on state parameter."""
        unauthed_tokens = self.session.get('_utoken')
        if not unauthed_tokens:
            raise AuthTokenError(self, 'Missing unauthorized token')

        data_token = self.data.get(self.OAUTH_TOKEN_PARAMETER_NAME)

        if data_token is None:
            raise AuthTokenError(self, 'Missing unauthorized token')

        token = None
        utoken = unauthed_tokens
        orig_utoken = utoken
        if not isinstance(utoken, dict):
            utoken = parse_qs(utoken)
        if utoken.get(self.OAUTH_TOKEN_PARAMETER_NAME) == data_token:
            token = utoken
        else:
            raise AuthTokenError(self, 'Incorrect tokens')
        return token

    def set_unauthorized_token(self):
        """
        Save unauthorized token in session.
        """
        self.session['_utoken'] = self.unauthorized_token()
        self.session.save()
        return self.session['_utoken']

    def get_or_create_state(self):
        """
        Save user id on session to pass to state parameter.
        """
        self.session = SessionStore()
        self.session['_user_id'] = self.data.get('user_id')
        self.session.create()

        return self.session.session_key

    def oauth_authorization_request(self, token):
        """Generate OAuth request to authorize token."""
        if not isinstance(token, dict):
            token = parse_qs(token)
        params = self.auth_extra_arguments() or {}
        params.update(self.get_scope_argument())
        params[self.OAUTH_TOKEN_PARAMETER_NAME] = token.get(
            self.OAUTH_TOKEN_PARAMETER_NAME
        )
        params['oauth_token_secret'] = token.get('oauth_token_secret')
        state = self.get_or_create_state()
        params[self.REDIRECT_URI_PARAMETER_NAME] = self.get_redirect_uri(state)
        return '{0}?{1}'.format(self.authorization_url(), urlencode(params))

    def get_redirect_uri(self, state=None):
        uri = self.redirect_uri
        if self.REDIRECT_STATE and state:
            uri = url_add_parameters(uri, {'state': state})
        return uri

    def auth_complete(self, *args, **kwargs):
        """Get user from state session."""
        state = self.validate_state()
        kwargs['user'] = User.objects.get(id=self.session['_user_id'])
        try:
            return super(RESTStateOAuth2Mixin, self).auth_complete(*args, **kwargs)
        except (AuthCanceled, AuthAlreadyAssociated, YoutubeChannelNotFound) as err:
            AuthError.objects.create(
                provider=self.name, user=kwargs['user'], message=str(err)
            )
            return redirect(reverse('user:redirect_to_app'))


class RESTTwitterOAuth(RESTStateOAuth2Mixin, TwitterOAuth):
    pass

class RESTStateInstagramOAuth2(RESTStateOAuth2Mixin, InstagramOAuth2):
    pass

class RESTStateLinkedinOAuth2(RESTStateOAuth2Mixin, LinkedinOAuth2):
    pass

class RESTStateGoogleOAuth2(RESTStateOAuth2Mixin, GoogleOAuth2):
    pass
