from django.urls import path
from src.core_auth import views

urlpatterns = [
    path('auth/register/', views.register_user, name='register'),
    path('auth/change_password/', views.change_password, name='change_password'),
    path('auth/me/tokens/', views.tokens_list, name='list_tokens'),
    path('auth/me/tokens/errors/', views.errors_list, name='list_errors'),
    path('auth/me/tokens/<provider>/', views.tokens_get, name='get_token'),

    path('profile/', views.profile_update, name='profile'),
    path('profile/me/', views.user_details, name='me'),
    path('profile/location/', views.location_update, name='location'),
    path('profile/tutorial/', views.tutorial_settings, name='tutorial'),

    path('social_profile/', views.social_profile_create, name='social_profile_create'),
    path('social_profile/<provider>/', views.social_profile_update_delete, name='social_profile_update_delete'),

    path('redirect_to_app/', views.redirect_user_to_app, name='redirect_to_app'),
    path('nearby_users/', views.nearby_users, name='nearby_users'),
]
