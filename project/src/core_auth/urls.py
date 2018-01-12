from django.urls import path
from src.core_auth import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('me/', views.user_details, name='me'),
    path('me/tokens/', views.tokens_list, name='list_tokens'),
    path('me/tokens/<provider>/', views.tokens_get, name='get_token'),
    path('redirect_to_app/', views.redirect_user_to_app, name='redirect_to_app'),
]
