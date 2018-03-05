import pytest
from model_mommy import mommy
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.urls import reverse

from rest_framework.test import APITestCase
from social_core.backends.oauth import BaseOAuth2
from social_core.exceptions import AuthTokenError, AuthCanceled

from src.core_auth.backends import RESTStateOAuth2Mixin
from src.core_auth.models import AuthError

User = get_user_model()

class RESTStateBackend(RESTStateOAuth2Mixin, BaseOAuth2):
    name = 'rest-state'

class RESTStateOAuth2MixinTests(APITestCase):
    @patch.object(RESTStateBackend, 'auth_url', return_value='http://redirect_url')
    def test_start_returns_response_with_redirect_url(self, auth_url):
        backend = RESTStateBackend()
        response = backend.start()
        auth_url.assert_called_once_with()
        assert isinstance(response, JsonResponse)

    @patch('src.core_auth.backends.SessionStore')
    def test_validate_state_sets_session(self, session):
        session.return_value = MagicMock()
        backend = RESTStateBackend()
        backend.data['state'] = 'session_key'
        backend.validate_state()
        session.assert_called_once_with(session_key='session_key')
        assert backend.session == session.return_value

    def test_get_unauthorized_token(self):
        session = {}
        session['_utoken'] = {'oauth_token': 'unauthed_token'}
        backend = RESTStateBackend()
        backend.OAUTH_TOKEN_PARAMETER_NAME = 'oauth_token'
        backend.data = {'oauth_token': 'unauthed_token'}
        backend.session = session
        token = backend.get_unauthorized_token()
        assert token == {'oauth_token': 'unauthed_token'}

    def test_get_unauthorized_token_is_None(self):
        session = {}
        session['_utoken'] = {}
        backend = RESTStateBackend()
        backend.OAUTH_TOKEN_PARAMETER_NAME = 'oauth_token'
        backend.data = {'oauth_token': 'unauthed_token'}
        backend.session = session
        with pytest.raises(AuthTokenError):
            token = backend.get_unauthorized_token()

    def test_get_unauthed_token_auth_token_error_if_tokens_mismatch(self):
        session = {}
        session['_utoken'] = {'oauth_token': 'unauthed_token'}
        backend = RESTStateBackend()
        backend.OAUTH_TOKEN_PARAMETER_NAME = 'oauth_token'
        backend.data = {'oauth_token': 'authed_token'}
        backend.session = session
        with pytest.raises(AuthTokenError):
            token = backend.get_unauthorized_token()

    def test_get_unauthed_token_auth_token_error_if_not_data_token(self):
        session = {}
        session['_utoken'] = {'oauth_token': 'unauthed_token'}
        backend = RESTStateBackend()
        backend.OAUTH_TOKEN_PARAMETER_NAME = 'oauth_token'
        backend.data = {'invalid_key': 'unauthed_token'}
        backend.session = session
        with pytest.raises(AuthTokenError):
            token = backend.get_unauthorized_token()

    def test_set_unauthed_token(self):
        backend = RESTStateBackend()
        backend.unauthorized_token = MagicMock()
        backend.unauthorized_token.return_value = 'unauthorized_token'
        session = MagicMock()
        backend.session = session

        token = backend.set_unauthorized_token()

        session.save.assert_called_once_with()
        assert token == session['_token']

    @patch('src.core_auth.backends.SessionStore')
    def test_get_or_create_state(self, session_class):
        session = MagicMock()
        session.session_key = '123456'
        session_class.return_value = session


        backend = RESTStateBackend()
        backend.data = {'user_id': 2}
        state = backend.get_or_create_state()

        session.create.assert_called_once_with()
        assert state == '123456'

    @patch.object(RESTStateBackend, 'auth_extra_arguments')
    @patch.object(RESTStateBackend, 'get_scope_argument')
    @patch.object(RESTStateBackend, 'get_or_create_state')
    @patch.object(RESTStateBackend, 'authorization_url')
    @patch.object(RESTStateBackend, 'get_redirect_uri')
    def test_oauth_authorization_request(self, redirect_uri, auth_url, state, scope_argument, auth_extra_arguments):
        auth_extra_arguments.return_value = {}
        scope_argument.return_value = {}
        state.return_value = 'state'
        auth_url.return_value = 'http://authorization_url'
        redirect_uri.return_value = 'http://redirect_uri'

        token = {'oauth_token': 'token', 'oauth_token_secret': 'token_secret'}
        backend = RESTStateBackend()
        backend.OAUTH_TOKEN_PARAMETER_NAME = 'oauth_token'
        backend.REDIRECT_URI_PARAMETER_NAME = 'redirect_uri'
        url = backend.oauth_authorization_request(token)

        assert url == 'http://authorization_url?oauth_token=token&oauth_token_secret=token_secret&redirect_uri=http%3A%2F%2Fredirect_uri'

    def test_get_redirect_uri(self):
        backend = RESTStateBackend()
        backend.redirect_uri = 'http://redirect_uri'
        backend.REDIRECT_STATE = True
        state = 'state'

        uri = backend.get_redirect_uri(state)

        assert uri == 'http://redirect_uri?state=state'

    @patch.object(RESTStateBackend, 'validate_state')
    @patch.object(BaseOAuth2, 'auth_complete')
    def test_auth_complete_injects_user_for_pipeline(self, super_auth_complete, validate_state):
        user = mommy.make(User)
        backend = RESTStateBackend()
        backend.session = {'_user_id': user.id}
        response = backend.auth_complete()
        validate_state.assert_called_once_with()
        super_auth_complete.assert_called_once_with(user=user)

    @patch.object(RESTStateBackend, 'validate_state')
    @patch.object(BaseOAuth2, 'auth_complete')
    def test_auth_complete_cancelation(self, super_auth_complete, validate_state):
        user = mommy.make(User)
        backend = RESTStateBackend()
        backend.session = {'_user_id': user.id}
        super_auth_complete.side_effect = AuthCanceled(backend)
        response = backend.auth_complete()
        assert response['location'] == reverse('user:redirect_to_app')
        validate_state.assert_called_once_with()
        super_auth_complete.assert_called_once_with(user=user)

        error_obj = AuthError.objects.last()
        assert error_obj.provider == 'rest-state'
        assert error_obj.message == 'Authentication process canceled'
        assert error_obj.user == user
