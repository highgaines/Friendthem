from django.urls import path
from src.core_auth import views

urlpatterns = [
    path('auth/register/', views.register_user, name='register'),
    path('profile/me/', views.user_details, name='me'),
    path('profile/hobbies/', views.update_hobbies, name='hobbies'),
    path('profile/location/', views.update_location, name='location'),
    path('auth/me/tokens/', views.tokens_list, name='list_tokens'),
    path('auth/me/tokens/<provider>/', views.tokens_get, name='get_token'),
    path('redirect_to_app/', views.redirect_user_to_app, name='redirect_to_app'),
]
