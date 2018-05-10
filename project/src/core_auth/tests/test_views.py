from model_mommy import mommy
from unittest.mock import Mock, patch
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry
from django.urls import reverse

from oauth2_provider.models import AccessToken
from src.core_auth.models import AuthError

User = get_user_model()

class RegisterUserViewTests(APITestCase):
    def setUp(self):
        self.application = mommy.make('Application', authorization_grant_type='password')
        self.url = reverse('user:register')

    def test_register_user_with_correct_data(self):
        data = {
            'client_id': self.application.client_id,
            'client_secret': self.application.client_secret,
            'grant_type': 'password',
            'username': 'xpto@example.com',
            'password': '123456',
        }
        response = self.client.post(self.url, data)
        content = response.json()

        assert 200 == response.status_code
        assert 'access_token' in content
        assert 'expires_in' in content
        assert 'scope' in content
        assert 'refresh_token' in content
        assert 'Bearer' == content['token_type']

        assert 1 == User.objects.count()
        user = User.objects.first()
        access_token = AccessToken.objects.get(token=content['access_token'])
        assert user == access_token.user

    def test_register_user_with_addional_data(self):
        data = {
            'client_id': self.application.client_id,
            'client_secret': self.application.client_secret,
            'grant_type': 'password',
            'username': 'xpto@example.com',
            'password': '123456',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(self.url, data)
        content = response.json()

        assert 200 == response.status_code
        assert 'access_token' in content
        assert 'expires_in' in content
        assert 'scope' in content
        assert 'refresh_token' in content
        assert 'Bearer' == content['token_type']

        assert 1 == User.objects.count()
        user = User.objects.first()
        access_token = AccessToken.objects.get(token=content['access_token'])
        assert user == access_token.user
        assert user.email == 'xpto@example.com'
        assert user.first_name == 'Test'
        assert user.last_name == 'User'

    def test_raises_400_if_invalid_application(self):
        data = {
            'client_id': 'invalid id',
            'client_secret': 'invalid secret',
            'grant_type': 'invalid grant',
            'username': 'xpto@example.com',
            'password': '123456',
        }
        response = self.client.post(self.url, data)
        content = response.json()

        assert 400 == response.status_code
        assert 0 == User.objects.count()

    def test_raises_400_if_user_already_exists(self):
        mommy.make(User, email='xpto@example.com')
        data = {
            'client_id': 'invalid id',
            'client_secret': 'invalid secret',
            'grant_type': 'invalid grant',
            'username': 'xpto@example.com',
            'password': '123456',
        }
        response = self.client.post(self.url, data)
        content = response.json()

        assert 400 == response.status_code
        assert 1 == User.objects.count()


class UserDetailViewTests(APITestCase):
    def setUp(self):
        self.user = mommy.make(User)
        social_profile = mommy.make('UserSocialAuth', user=self.user)
        self.client.force_authenticate(self.user)
        self.url = reverse('user:me')

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        assert 401 == response.status_code

    def test_returns_correct_data_for_user(self):
        response = self.client.get(self.url)
        assert 200 == response.status_code

        content = response.json()
        assert self.user.email == content['email']
        assert self.user.id == content['id']
        assert None == content['hobbies']
        assert 'social_profiles' in content
        assert 1 == len(content['social_profiles'])


class AutheErrorViewTests(APITestCase):
    def setUp(self):
        self.user = mommy.make(User)
        self.auth_error = mommy.make('AuthError', user=self.user)

        self.client.force_authenticate(self.user)
        self.url = reverse('user:list_errors')

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        assert 401 == response.status_code

    def test_list_errors_for_user(self):
        response = self.client.get(self.url)
        assert 200 == response.status_code

        content = response.json()
        assert isinstance(content, list)
        assert 1 == len(content)

        assert {
            'provider': self.auth_error.provider,
            'message': self.auth_error.message,
        } == content[0]

        assert AuthError.objects.filter(user=self.user).exists() is False


class TokensViewTests(APITestCase):
    def setUp(self):
        self.user = mommy.make(User)
        other_user = mommy.make(User)
        other_auth_user = mommy.make('UserSocialAuth', provider='facebook')
        self.facebook_user = mommy.make(
            'UserSocialAuth', user=self.user, provider='facebook',
            extra_data={
                'access_token': 'AAAAaaaaa',
                'auth_time': 123456,
                'expires': 123124,
            }
        )
        self.google_user = mommy.make(
            'UserSocialAuth', user=self.user, provider='google-oauth2',
            extra_data={
                'access_token': 'BBBBBaaaaa',
                'auth_time': 123789,
                'expires': 12789,
            }
        )

        self.instagram_user = mommy.make(
            'UserSocialAuth', user=self.user, provider='instagram',
            extra_data={
                'access_token': 'bbbbBBBaaaaa',
                'auth_time': 124789,
                'expires': 12786,
            }
        )
        self.linkedin_user = mommy.make(
            'UserSocialAuth', user=self.user, provider='linkedin-oauth2',
            extra_data={
                'access_token': 'bbbbBBBaaaab',
                'auth_time': 124779,
                'expires': 12783,
            }
        )
        self.twitter_user = mommy.make(
            'UserSocialAuth', user=self.user, provider='twitter',
            extra_data={
                'access_token': {
                    'oauth_token': 'bAba', 'oauth_token_secret': 'cDba', 'x_auth_expires': 12733},
                'auth_time': 312312,
            }
        )
        self.client.force_authenticate(self.user)
        self.url = reverse('user:list_tokens')

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        assert 401 == response.status_code

    def test_list_tokens_for_user(self):
        response = self.client.get(self.url)
        assert 200 == response.status_code

        content = response.json()
        assert isinstance(content, list)
        assert 5 == len(content)

        assert sorted([
            'facebook', 'twitter', 'linkedin-oauth2',
            'instagram', 'google-oauth2'
        ]) == sorted([x['provider'] for x in content])

        assert {
            'provider': 'twitter',
            'access_token': {
                'oauth_token': 'bAba', 'oauth_token_secret': 'cDba', 'x_auth_expires': 12733},
            'expires': 12733,
            'auth_time': 312312,
        } == [x for x in content if x['provider'] == 'twitter'][0]

        assert {
            'provider': 'facebook',
            'access_token': 'AAAAaaaaa',
            'auth_time': 123456,
            'expires': 123124,
        } == [x for x in content if x['provider'] == 'facebook'][0]

        assert {
            'provider': 'linkedin-oauth2',
            'access_token': 'bbbbBBBaaaab',
            'auth_time': 124779,
            'expires': 12783,
        } == [x for x in content if x['provider'] == 'linkedin-oauth2'][0]

        assert {
            'provider': 'google-oauth2',
            'access_token': 'BBBBBaaaaa',
            'auth_time': 123789,
            'expires': 12789,
        } == [x for x in content if x['provider'] == 'google-oauth2'][0]

        assert {
            'provider': 'instagram',
            'access_token': 'bbbbBBBaaaaa',
            'auth_time': 124789,
            'expires': None,
        } == [x for x in content if x['provider'] == 'instagram'][0]

    def test_get_tokens_for_user_and_provider(self):
        response = self.client.get(reverse('user:get_token', kwargs={'provider': 'facebook'}))
        assert 200 == response.status_code

        content = response.json()
        assert isinstance(content, dict)
        assert {
            'provider': 'facebook',
            'access_token': 'AAAAaaaaa',
            'auth_time': 123456,
            'expires': 123124,
        } == content


class UpdateProfileViewTests(APITestCase):
    def setUp(self):
        self.user = mommy.make(User)
        self.client.force_authenticate(self.user)
        self.url = reverse('user:profile')

    def test_login_required(self):
        self.client.logout()
        response = self.client.put(self.url)
        assert 401 == response.status_code

    def test_update_profile(self):
        data = {
            'hobbies': ['Music', 'Chess'],
            'phone_number': '+5541999999999',
            'hometown': 'New York',
            'occupation': 'Test Occupation',
            'age': 33,
            'personal_email': 'test@example.com',
            'phone_is_private': True,
            'email_is_private': True,
        }
        response = self.client.put(self.url, data=data)
        user = User.objects.get(id=self.user.id)
        assert 200 == response.status_code
        assert data['hobbies'] == user.hobbies
        assert data['phone_number'] == user.phone_number
        assert data['hometown'] == user.hometown
        assert data['occupation'] == user.occupation
        assert data['age'] == user.age
        assert data['personal_email'] == user.personal_email
        assert data['phone_is_private'] is True
        assert data['email_is_private'] is True

    def test_update_overrides_old_profile(self):
        self.user.hobbies = ['Shaolin Shadowboxing']
        self.user.save()
        data = {
            'hobbies': ['Music', 'Chess'],
            'phone_number': '+5541999999999',
            'hometown': 'New York',
            'occupation': 'Test Occupation',
            'age': 33,
            'personal_email': 'test@example.com'
        }
        response = self.client.put(self.url, data=data)
        user = User.objects.get(id=self.user.id)
        assert 200 == response.status_code
        assert data['hobbies'] == user.hobbies
        assert data['phone_number'] == user.phone_number
        assert data['hometown'] == user.hometown
        assert data['occupation'] == user.occupation
        assert data['age'] == user.age
        assert data['personal_email'] == user.personal_email

    def test_patch_updates_only_present_fields(self):
        self.user.hobbies = ['Shaolin Shadowboxing']
        self.user.save()
        data = {
            'hometown': 'New York',
            'occupation': 'Test Occupation',
        }
        response = self.client.patch(self.url, data=data)
        user = User.objects.get(id=self.user.id)
        assert 200 == response.status_code
        assert ['Shaolin Shadowboxing'] == user.hobbies
        assert data['hometown'] == user.hometown
        assert data['occupation'] == user.occupation


class TutorialViewTests(APITestCase):
    def setUp(self):
        self.user = mommy.make(User)
        self.client.force_authenticate(self.user)
        self.url = reverse('user:tutorial')

    def test_login_required(self):
        self.client.logout()
        response = self.client.put(self.url)
        assert 401 == response.status_code

    def test_update_tutorial_settings(self):
        data = {
            'invite_tutorial': True,
            'connection_tutorial': False,
            'tutorial_complete': False,
        }
        response = self.client.put(self.url, data=data)
        user = User.objects.get(id=self.user.id)
        assert 200 == response.status_code
        assert data['invite_tutorial'] == user.invite_tutorial is True
        assert data['connection_tutorial'] == user.connection_tutorial is False
        assert data['tutorial_complete'] == user.tutorial_complete is False

    def test_update_overrides_old_profile(self):
        self.user.connection_tutorial = True
        self.user.save()
        data = {
            'invite_tutorial': True,
            'connection_tutorial': False,
            'tutorial_complete': False,
        }
        response = self.client.put(self.url, data=data)
        user = User.objects.get(id=self.user.id)
        assert data['invite_tutorial'] == user.invite_tutorial is True
        assert data['connection_tutorial'] == user.connection_tutorial is False
        assert data['tutorial_complete'] == user.tutorial_complete is False

    def test_patch_updates_only_present_fields(self):
        self.user.connection_tutorial = True
        self.user.save()
        data = {
            'connection_tutorial': False,
        }
        response = self.client.patch(self.url, data=data)
        user = User.objects.get(id=self.user.id)
        assert 200 == response.status_code
        assert user.invite_tutorial is False
        assert data['connection_tutorial'] == user.connection_tutorial is False
        assert user.tutorial_complete is False


class CreateSocialProfileViewTestCase(APITestCase):
    def setUp(self):
        self.user = mommy.make(User)
        self.client.force_authenticate(self.user)
        self.url = reverse('user:social_profile_create')

    def test_login_required(self):
        self.client.logout()
        response = self.client.post(self.url)
        assert 401 == response.status_code

    def test_create_social_profile_for_user(self):
        data = {'provider': 'snapchat', 'username': 'testuser'}
        response = self.client.post(self.url, data=data)

        assert 201 == response.status_code
        social_profile = self.user.social_auth.get(provider='snapchat')
        assert 'testuser' == social_profile.extra_data['username']
        assert 'testuser' == social_profile.uid

    def test_raises_400_if_social_auth_with_uid_already_exists(self):
        social_auth = mommy.make('UserSocialAuth', provider='snapchat', uid='test_user')
        data = {'provider': 'snapchat', 'username': 'test_user'}

        response = self.client.post(self.url, data=data)

        assert 400 == response.status_code
        assert {'non_field_errors': ['User "test_user" already exists in "snapchat".']} == response.json()

    def test_raises_400_if_social_auth_for_user_already_exists(self):
        social_auth = mommy.make('UserSocialAuth', provider='snapchat', user=self.user)
        data = {'provider': 'snapchat', 'username': 'test_user'}

        response = self.client.post(self.url, data=data)

        assert 400 == response.status_code
        assert {'non_field_errors': ['Social Profile for this user already exists for provider "snapchat".']} == response.json()


class UpdateSocialProfileViewTestCase(APITestCase):
    def setUp(self):
        self.user = mommy.make(User)
        self.social_auth = mommy.make('UserSocialAuth', user=self.user, provider='snapchat')
        self.client.force_authenticate(self.user)
        self.url = reverse('user:social_profile_update_delete', kwargs={'provider': 'snapchat'})

    def test_login_required(self):
        self.client.logout()
        response = self.client.put(self.url)
        assert 401 == response.status_code

    def test_update_social_profile_for_user(self):
        data = {'username': 'testuser'}
        response = self.client.put(self.url, data=data)

        assert 200 == response.status_code
        social_profile = self.user.social_auth.get(provider='snapchat')
        assert 'testuser' == social_profile.extra_data['username']
        assert 'testuser' == social_profile.uid

    def test_raises_400_if_social_auth_with_uid_already_exists(self):
        social_auth = mommy.make('UserSocialAuth', provider='snapchat', uid='test_user')
        data = {'username': 'test_user'}

        response = self.client.put(self.url, data=data)

        assert 400 == response.status_code
        assert {'non_field_errors': ['User "test_user" already exists in "snapchat".']} == response.json()


class DeleteSocialProfileViewTestCase(APITestCase):
    def setUp(self):
        self.user = mommy.make(User)
        self.social_auth = mommy.make('UserSocialAuth', user=self.user, provider='snapchat')
        self.client.force_authenticate(self.user)
        self.url = reverse('user:social_profile_update_delete', kwargs={'provider': 'snapchat'})

    def test_login_required(self):
        self.client.logout()
        response = self.client.delete(self.url)
        assert 401 == response.status_code

    def test_delete_social_profile_for_provider(self):
        response = self.client.delete(self.url)

        assert 204 == response.status_code
        social_profile = self.user.social_auth.filter(provider='snapchat').exists() is False


class UpdateLocationTests(APITestCase):
    def setUp(self):
        self.user = mommy.make(User)
        self.client.force_authenticate(self.user)
        self.url = reverse('user:location')

    def test_login_required(self):
        self.client.logout()
        response = self.client.put(self.url)
        assert 401 == response.status_code

    @patch('src.core_auth.serializers.googlemaps')
    def test_update_location(self, mocked_gmaps):
        gmaps_client = Mock()
        gmaps_client.reverse_geocode.return_value = [{
            'formatted_address': 'Sesame Street, 0',
            'types': ['locality', 'political']
        }]
        mocked_gmaps.Client.return_value = gmaps_client
        data = {'last_location': {'lat':1, 'lng': 2}}
        response = self.client.put(self.url, data=data, format='json')
        user = User.objects.get(id=self.user.id)
        assert 200 == response.status_code
        assert 2 == user.last_location.x
        assert 1 == user.last_location.y
        assert 'Sesame Street, 0' == user.address

    @patch('src.core_auth.serializers.googlemaps')
    def test_update_location_overrides_old_location(self, mocked_gmaps):
        gmaps_client = Mock()
        gmaps_client.reverse_geocode.return_value = [{
            'formatted_address': 'Sesame Street, 0',
            'types': ['locality', 'political']
        }]
        mocked_gmaps.Client.return_value = gmaps_client
        self.user.last_location = GEOSGeometry('POINT (2 1)')
        self.user.save()
        data = {'last_location': {'lng': 1, 'lat': 2}}
        response = self.client.put(self.url, data=data, format='json')
        user = User.objects.get(id=self.user.id)
        assert 200 == response.status_code
        assert 1 == user.last_location.x
        assert 2 == user.last_location.y
        assert 'Sesame Street, 0' == user.address

    @patch('src.core_auth.serializers.googlemaps')
    def test_deletes_location_if_none_is_sent(self, mocked_gmaps):
        gmaps_client = Mock()
        mocked_gmaps.Client.return_value = gmaps_client
        self.user.last_location = GEOSGeometry('POINT (2 1)')
        self.user.save()
        data = {'last_location': None}
        response = self.client.put(self.url, data=data, format='json')
        user = User.objects.get(id=self.user.id)

        gmaps_client.assert_not_called()
        assert 200 == response.status_code
        assert user.last_location is None
        assert user.address == None

    @patch('src.core_auth.serializers.googlemaps')
    def test_sets_address_to_none_if_no_address_is_not_provided(self, mocked_gmaps):
        gmaps_client = Mock()
        gmaps_client.reverse_geocode.return_value = []
        mocked_gmaps.Client.return_value = gmaps_client
        self.user.last_location = GEOSGeometry('POINT (2 1)')
        self.user.save()
        data = {'last_location': {'lng': 1, 'lat': 2}}
        response = self.client.put(self.url, data=data, format='json')
        user = User.objects.get(id=self.user.id)
        assert 200 == response.status_code
        assert 1 == user.last_location.x
        assert 2 == user.last_location.y
        assert user.address is None


    def test_returns_400_for_incorrect_data(self):
        data = {'last_location': {'lrg': 1, 'lat': 2}}
        response = self.client.put(self.url, data=data, format='json')
        user = User.objects.get(id=self.user.id)
        assert 400 == response.status_code
        assert 'Point must have `lng` and `lat` keys.' == response.json()['last_location'][0]


class NearbyUsersViewTestCase(APITestCase):
    def setUp(self):
        self.user = mommy.make(User, last_location=GEOSGeometry('POINT (0 0)'))
        mommy.make('UserSocialAuth', user=self.user)
        self.client.force_authenticate(self.user)
        self.url = reverse('user:nearby_users')

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        assert 401 == response.status_code

    def test_get_nearby_users(self):
        other_user_1 = mommy.make(
            User,
            last_location=GEOSGeometry('POINT (0.0001 0)'),
            phone_number='+552133333333', phone_is_private=False,
            email_is_private=False, ghost_mode=False, featured=False,
            _fill_optional=True, picture=None
        )
        ghost_user = mommy.make(User, last_location=GEOSGeometry('POINT (0.0001 0)'), ghost_mode=True)
        mommy.make('UserSocialAuth', user=other_user_1)
        mommy.make('Connection', user_1=self.user, user_2=other_user_1)
        other_user_2 = mommy.make(User, last_location=GEOSGeometry('POINT (0.0001 0)'), picture='http://example.com')
        response = self.client.get(self.url + '?miles=200')
        assert 200 == response.status_code

        assert 2 == len(response.json())
        other_user_data = response.json()[1]

        assert other_user_data['id'] == other_user_1.id
        assert 'distance' in other_user_data
        assert 0.006917072471764893 == other_user_data['distance']
        assert 100 == other_user_data['connection_percentage']
        assert 'sent' == other_user_data['category']
        assert other_user_data['phone_number'] == other_user_1.phone_number.as_e164
        assert other_user_data['personal_email'] == other_user_1.personal_email

    def test_get_nearby_and_featured_users(self):
        other_user_1 = mommy.make(
            User,
            last_location=GEOSGeometry('POINT (0.0001 0)'),
            phone_number='+552133333333', phone_is_private=False,
            email_is_private=False, featured=False, ghost_mode=False,
            _fill_optional=True
        )
        ghost_user = mommy.make(User, last_location=GEOSGeometry('POINT (0.0001 0)'), ghost_mode=True)
        mommy.make('UserSocialAuth', user=other_user_1)
        mommy.make('Connection', user_1=self.user, user_2=other_user_1)
        other_user_2 = mommy.make(User, last_location=GEOSGeometry('POINT (20 0)'))
        featured_user = mommy.make(
            User, featured=True, email_is_private=True, phone_is_private=True,
            last_location=None, phone_number='+552122222222', ghost_mode=False,
            _fill_optional=True,
        )
        response = self.client.get(self.url + '?miles=200')
        assert 200 == response.status_code

        assert 2 == len(response.json())
        other_user_data = response.json()[0]
        featured_user_data = response.json()[1]

        assert other_user_data['id'] == other_user_1.id
        assert 'distance' in other_user_data
        assert 0.006917072471764893 == other_user_data['distance']
        assert 100 == other_user_data['connection_percentage']
        assert other_user_data['phone_number'] == other_user_1.phone_number.as_e164
        assert other_user_data['personal_email'] == other_user_1.personal_email
        assert other_user_data['featured'] is False
        assert featured_user_data['id'] == featured_user.id
        assert featured_user_data['phone_number'] is None
        assert featured_user_data['personal_email'] is None
        assert featured_user_data['featured'] is True

    def test_get_only_featured_users_for_user_without_last_location(self):
        self.user.last_location = None
        self.user.save()
        other_user_1 = mommy.make(
            User,
            last_location=GEOSGeometry('POINT (0.0001 0)'),
            phone_number='+552133333333', phone_is_private=False,
            email_is_private=False, featured=False,
            _fill_optional=True
        )
        ghost_user = mommy.make(
            User,
            last_location=GEOSGeometry('POINT (0.0001 0)'),
            ghost_mode=True
        )
        mommy.make('UserSocialAuth', user=other_user_1)
        mommy.make('Connection', user_1=self.user, user_2=other_user_1)
        other_user_2 = mommy.make(User, last_location=GEOSGeometry('POINT (20 0)'))
        featured_user = mommy.make(
            User, featured=True, email_is_private=True, phone_is_private=True,
            last_location=None, phone_number='+552122222222',
            _fill_optional=True,
        )
        response = self.client.get(self.url + '?miles=200')
        assert 200 == response.status_code

        assert 1 == len(response.json())
        featured_user_data = response.json()[0]

        assert featured_user_data['id'] == featured_user.id
        assert featured_user_data['phone_number'] is None
        assert featured_user_data['personal_email'] is None
        assert featured_user_data['featured'] is True

class ChangePasswordViewTests(APITestCase):
    def setUp(self):
        self.application = mommy.make(
            'Application',
            authorization_grant_type='password'
        )
        self.user = mommy.make(User)
        self.user.set_password('test123!')
        self.user.save()

        mommy.make('UserSocialAuth', user=self.user)
        self.client.force_authenticate(self.user)
        self.url = reverse('user:change_password')

    def test_login_required(self):
        self.client.logout()
        response = self.client.post(self.url)
        assert 401 == response.status_code

    def test_change_password_success(self):
        data = {
            'old_password': 'test123!', 'new_password': '123test!',
            'client_id': self.application.client_id,
            'client_secret': self.application.client_secret,
        }
        response = self.client.post(self.url, data)
        assert 200 == response.status_code
        assert response.json()['email'] == self.user.email
        assert 1 == len(response.json()['social_profiles'])
        self.user.refresh_from_db()
        assert self.user.check_password('123test!') is True

    def test_change_password_fail_if_client_is_invalid(self):
        data = {
            'old_password': 'test123!', 'new_password': '123test!',
            'client_id': 'invalid_client_id',
            'client_secret': self.application.client_secret,
        }
        response = self.client.post(self.url, data)
        assert 400 == response.status_code
        assert response.json() == {'non_field_errors': ['Application not found.']}
        self.user.refresh_from_db()
        assert self.user.check_password('test123!') is True

    def test_change_password_fail_if_old_password_dont_match(self):
        data = {
            'old_password': 'test123', 'new_password': '123test!',
            'client_id': self.application.client_id,
            'client_secret': self.application.client_secret,
        }
        response = self.client.post(self.url, data)
        assert 400 == response.status_code
        assert response.json() == {'old_password':
            ['Your old password was entered incorrectly. Please enter it again.']
        }
        self.user.refresh_from_db()
        assert self.user.check_password('test123!') is True


class RedirectToAppViewTests(APITestCase):
    def test_view_redirects_to_app(self):
        response = self.client.get(reverse('user:redirect_to_app'))
        assert 302 == response.status_code
        assert 'FriendThem://' == response['Location']
