from six.moves.urllib_parse import urlencode
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.db import SessionStore
from rest_framework.response import Response
from rest_framework.decorators import api_view
from social_core.backends.instagram import InstagramOAuth2
from social_core.backends.linkedin import LinkedinOAuth2
from social_core.backends.twitter import TwitterOAuth
from social_core.utils import url_add_parameters, parse_qs

User = get_user_model()

class RESTStateOAuth2Mixin(object):
    def validate_state(self):
        state = SessionStore(session_key=self.data.get('state'))
        return state

    def get_unauthorized_token(self):
        unauthed_tokens = self.state.get('_utoken')
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
        self.session['_utoken'] = self.unauthorized_token()
        self.session.save()
        return self.session['_utoken']

    def get_or_create_state(self):
        self.session = SessionStore()
        self.session['_user_id'] = self.data.get('user_id')
        self.session.create()

        return self.session.session_key

    def start(self):
        return JsonResponse({'redirect_url': self.auth_url()})

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
        self.state = self.validate_state()
        kwargs['user'] = User.objects.get(id=self.state['_user_id'])
        return super(RESTStateOAuth2Mixin, self).auth_complete(*args, **kwargs)


class RESTTwitterOAuth(RESTStateOAuth2Mixin, TwitterOAuth):
    pass

class RESTStateInstagramOAuth2(RESTStateOAuth2Mixin, InstagramOAuth2):
    pass

class RESTStateLinkedinOAuth2(RESTStateOAuth2Mixin, LinkedinOAuth2):
    pass
