from django.urls import path
from src.core_auth import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('me/', views.user_details, name='me'),
    path('redirect_to_app/', views.redirect_user_to_app, name='redirect_to_app'),
]
