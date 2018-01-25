from model_mommy import mommy
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry
from django.urls import reverse

from oauth2_provider.models import AccessToken

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
        social_profile = mommy.make('SocialProfile', user=self.user)
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



class UpdateLocationTests(APITestCase):
    def setUp(self):
        self.user = mommy.make(User)
        self.client.force_authenticate(self.user)
        self.url = reverse('user:location')

    def test_login_required(self):
        self.client.logout()
        response = self.client.put(self.url)
        assert 401 == response.status_code

    def test_update_location(self):
        data = {'last_location': {'lat':1, 'lng': 2}}
        response = self.client.put(self.url, data=data, format='json')
        user = User.objects.get(id=self.user.id)
        assert 200 == response.status_code
        assert 2 == user.last_location.x
        assert 1 == user.last_location.y

    def test_update_location_overrides_old_location(self):
        self.user.last_location = GEOSGeometry('POINT (2 1)')
        self.user.save()
        data = {'last_location': {'lng': 1, 'lat': 2}}
        response = self.client.put(self.url, data=data, format='json')
        user = User.objects.get(id=self.user.id)
        assert 200 == response.status_code
        assert 1 == user.last_location.x
        assert 2 == user.last_location.y

    def test_returns_400_for_incorrect_data(self):
        data = {'last_location': {'lrg': 1, 'lat': 2}}
        response = self.client.put(self.url, data=data, format='json')
        user = User.objects.get(id=self.user.id)
        assert 400 == response.status_code
        assert 'Point must have `lng` and `lat` keys.' == response.json()['last_location'][0]


class NearbyUsersView(APITestCase):
    def setUp(self):
        self.user = mommy.make(User, last_location=GEOSGeometry('POINT (0 0)'))
        self.client.force_authenticate(self.user)
        self.url = reverse('user:nearby_users')

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        assert 401 == response.status_code

    def test_get_nearby_users(self):
        other_user_1 = mommy.make(User, last_location=GEOSGeometry('POINT (0.0001 0)'))
        other_user_2 = mommy.make(User, last_location=GEOSGeometry('POINT (20 0)'))
        response = self.client.get(self.url + '?miles=200')
        assert 200 == response.status_code

        assert 1 == len(response.json())
        other_user_data = response.json()[0]

        assert other_user_data['id'] == other_user_1.id
        assert 'distance' in other_user_data
        assert 0.006917072471764893 == other_user_data['distance']


class RedirectToAppViewTests(APITestCase):
    def test_view_redirects_to_app(self):
        response = self.client.get(reverse('user:redirect_to_app'))
        assert 302 == response.status_code
        assert 'FriendThem://' == response['Location']
